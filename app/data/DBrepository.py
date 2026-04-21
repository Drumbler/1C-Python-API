from typing import Dict, List
import psycopg2
from logging import getLogger
from fastapi import HTTPException, UploadFile
import pandas as pd
from dotenv import load_dotenv

from app.controllers.module_loader import load_all_modules
import os


logger = getLogger(__name__)



class DBRepository:

    # name pass and user for local usage only!
    def __init__(self):
        
        # self.conn_data = {'dbname': str(os.environ.get('DB_NAME')),
        #                   'user': str(os.environ.get('DB_USER')),
        #                   'password': str(os.environ.get('DB_PASS')),
        #                   'host': str(os.environ.get('DB_IP')),
        #                   'port': str(os.environ.get('DB_PORT')),
        #                   }
        '''
        Строка ниже нужна для подключения к базе при запуске api локально на своей машине(ПК)
        '''
        load_dotenv()
        self.conn_data = {'dbname': str(os.getenv('DB_NAME')),
                          'user': str(os.getenv('DB_USER')),
                          'password': str(os.getenv('DB_PASS')),
                          'host': str(os.getenv('DB_IP')),
                          'port': str(os.getenv('DB_PORT')),
                          }
    
    def get_module_file_location(self, series: str) -> str:
        if not series:
            raise RuntimeError("Series cannot be empty")
        with psycopg2.connect(**self.conn_data,) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT file_name FROM product_mapping
                    JOIN products on products.file_loc=product_mapping.id
                    WHERE products.series=(%s)
                            """, (series,))
                results = cur.fetchone()[0]
        return results

    def get_materials_for_products(self, series: str) -> Dict[int, List]:
        '''
        Метод, выгружающий список материалов из базы данных для конкретного изделия.
        Материалы определяются по серии и записаны в базу данных.
        '''

        if not series:
            raise RuntimeError("Series cannot be empty")
        with psycopg2.connect(**self.conn_data,) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT m.id, m.abbreviation, m.name, mfp.misc, m.price * mfp.quantity AS total_price, mfp.alternative_abbreviations
                    FROM products p
                    JOIN materials_for_products mfp ON p.id = mfp.product_id
                    JOIN materials m ON mfp.material_id = m.id
                    WHERE p.series = (%s);
                """, (series, ))
                results = cur.fetchall()

        materials_dict = {}
        for row in results:
            material_id, abbreviation, name, misc, total_price, alternative_abbreviations = row

            abbreviations_to_use = set()
            if abbreviation:
                abbreviations_to_use.add(abbreviation.strip())
            if alternative_abbreviations:
                abbreviations_to_use.update(
                    abbr.strip()
                    for abbr in alternative_abbreviations.split(",")
                    if abbr.strip()
                )

            materials_dict[material_id] = [
                abbreviations_to_use,
                name,
                misc,
                float(total_price)
            ]
        return materials_dict

    def get_parameters_for_db(
            self,
            list_requered_parameters: list,
            key_column_for_parameters="material_name",
            name_of_db_table="materials",
            list_of_column_names: list = ['id', "material_name", "price"],
            requered_filter="Type IN (\'material\', \'work\', \'semis\')") -> Dict:
        '''
        Метод, для получения данных из базы данных, реализована возможность выбора по какому столбцу идет выгрузка 
        и какие столбцы выгрузить
        '''
        if not list_of_column_names:
            return {"Error": "List of column names cannot be empty"}

        column_name_string = ", ".join(list_of_column_names)

        if requered_filter:
            full_filter = f"{requered_filter} AND {key_column_for_parameters} IN ({','.join(['%s'] * len(list_requered_parameters))})"
        else:
            full_filter = f"{key_column_for_parameters} IN ({','.join(['%s'] * len(list_requered_parameters))})"

        query = f"SELECT {column_name_string} FROM {name_of_db_table} WHERE {full_filter}"

        try:
            with psycopg2.connect(**self.conn_data) as conn:
                with conn.cursor() as cur:
                    cur.execute(query, list_requered_parameters)
                    results = cur.fetchall()

            match len(list_of_column_names):
                case 1:
                    return [row[0] for row in results]
                case _:
                    return {row[0]: list(row[1:]) for row in results}

        except psycopg2.Error as e:
            logger.warning(f"Database error: {e}")
            raise RuntimeError(f"Database error: {e}")
        except Exception as e:
            logger.error(f"Unhandled exception during calculation: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    def add_data_from_excel(self, excel_file: UploadFile):
        '''
        Метод добавления данных в базу данных из таблицы excel
        '''
        rename_dict = {
            'Наименование': 'name',
            'Ед.измерения': 'units',
            'Площадь': 'to_weight_koef',
            'Цена по прайсу (м2, п. метр)': 'price',
        }
        try:
            excel_file.file.seek(0)
            data_to_add = pd.read_excel(excel_file.file)
        except FileNotFoundError as e:
            raise FileNotFoundError(f'File not found {e}')
        except Exception as e:
            raise Exception(f'Error while reading excel {e}')

        data_to_add = data_to_add.rename(columns=rename_dict)
        with psycopg2.connect(**self.conn_data) as conn:
            with conn.cursor() as cur:
                cur.execute('Select name FROM materials')
                db_names = set(row[0] for row in self.cursor.fetchall())
        indices_to_drop = []
        for _, row in data_to_add.iterrows():
            name = row['Name']
            if name in db_names:
                logger.warning(f'Duplicate entry for {name}, skipping...')
                continue
            try:
                with psycopg2.connect(**self.conn_data) as conn:
                    with conn.cursor() as cur:
                        cur.execute(
                            'INSERT INTO materials(name, units, price, type, to_weight_koef) VALUES (%s, %s, %s, %s, %s)',
                            (row['name'], row['units'], row['price'], row['type'],
                             'material' if row['units'] == 'м2' else 'semis')
                        )
                    indices_to_drop.append(
                        data_to_add[data_to_add['name'] == name].index)
            except psycopg2.IntegrityError:
                logger.warning(f'Duplicate entry for {name}, skipping...')
                continue
            except psycopg2.Error as e:
                logger.warning(f'Database error: {e}')
                raise RuntimeError(f"Database error: {e}")
        data_to_add.drop(indices_to_drop, inplace=True)

    def update_materials(self, data_from_excel: pd.DataFrame):
        '''
        Метод 
        '''
        try:
            data_from_excel.drop_duplicates('Material', inplace=True)
            with psycopg2.connect(**self.conn_data) as conn:
                for _, row in data_from_excel.iterrows():
                    conn.cursor().execute("UPDATE materials SET Price = %s WHERE Name = %s",
                                          (row['Material_Price'], row['Material']))

        except psycopg2.Error as e:
            logger.warning(f"Database error: {e}")
            raise RuntimeError(f"Database error: {e}")
        except Exception as e:
            logger.warning(f"Error while updating materials: {e}")
            raise RuntimeError(f"Error while updating materials: {e}")

    def update_components(self):
        '''
        Метод класса для обновления цен на "сложные материалы", т.е. для сборных материалов, 
        таких как агрегат на холодильные столы и glassier
        '''
        modules = load_all_modules()
        if not modules:
            raise RuntimeError('No modules found')

        for module_name, module in modules.items():
            new_price = module.calculate()
            try:
                with psycopg2.connect(**self.conn_data) as conn:
                    with conn.cursor() as cur:
                        cur.execute("UPDATE materials SET Price = %s WHERE Name = %s",
                                    (round(new_price, 2), module_name))
                    logger.info(
                        f"Updated module {module_name} with price {new_price}"
                    )
            except psycopg2.Error as e:
                logger.warning(f"Database error: {e}")
                raise RuntimeError(f"Database error: {e}")

    def update_data_from_excel(self, excel_file: UploadFile):
        '''
        Метод для обновления данных в таблице материлов, из таблицы excel 
        '''
        rename_dict = {
            'Наименование': 'name',
            'Ед.измерения': 'units',
            'Площадь': 'to_weight_koef',
            'Стоимость 1 шт': 'price',
            'Цена по прайсу (м2, п. метр)': 'Material_price',
            'Материал': 'Material',
        }

        try:
            data_to_add = pd.read_excel(excel_file.file)
        except FileNotFoundError as e:
            logger.warning(f'File not found {e}')
            raise FileNotFoundError(f'File not found {e}')
        except Exception as e:
            raise Exception(f'Error while reading excel {e}')

        not_updated_data = []
        missing_in_db = []
        data_to_add = data_to_add.rename(columns=rename_dict)
        try:
            with psycopg2.connect(**self.conn_data) as conn:
                with conn.cursor() as cur:
                    cur.execute('SELECT name FROM materials')
                    db_data = cur.fetchall()
                db_names = set(row[0] for row in db_data)
                self.update_materials(data_to_add)
                for _, row in data_to_add.iterrows():
                    name = row['name']
                    if name not in db_names:
                        missing_in_db.append(name)
                    else:
                        try:
                            with conn.cursor() as cur:
                                cur.execute(
                                    "UPDATE materials SET Price = %s WHERE Name = %s",
                                    (row['price'], name))
                                added_row = data_to_add[
                                    data_to_add['name'] == name].index
                            data_to_add.drop(added_row, inplace=True)
                        except Exception as e:
                            not_updated_data.append(name)
                            logger.warning(f'Database error: {e}')
                            continue

        except psycopg2.Error as e:
            logger.warning(f"Database error: {e}")
            raise RuntimeError(f'Database error: {e}')
        self.update_components()
        if not data_to_add.empty:
            pd.DataFrame(data_to_add).to_excel(
                'No_such_table_in_DB.xlsx', index=False
            )
        pd.DataFrame(not_updated_data).to_excel(
            'Not_updated_in_DB.xlsx', index=False
        )

    def get_number_of_rows(self):
        '''
        Метод для получения количества записей
        '''
        try:
            with psycopg2.connect(**self.conn_data) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT COUNT(*) FROM materials")
                    count = cur.fetchall()
                return count
        except psycopg2.Error as e:
            logger.warning(f'Database error: {e}')
            raise RuntimeError(f"Database error: {e}")


dbrepo = DBRepository()
