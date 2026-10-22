#!/usr/bin/env bash
set -Eeuo pipefail

readonly project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
readonly compose_file="${COMPOSE_FILE:-compose.production.yaml}"
readonly image_repository="${API_IMAGE_REPOSITORY:-ghcr.io/drumbler/1c-python-api}"
readonly image_tag="${1:-}"

cd "${project_dir}"

if [[ ! "${image_tag}" =~ ^sha-[0-9a-f]{40}$ ]]; then
    echo "Usage: $0 sha-<full-40-character-git-commit>" >&2
    exit 2
fi

if [[ ! -f .env ]]; then
    echo "Missing .env in $(pwd)" >&2
    exit 2
fi

export API_IMAGE="${image_repository}:${image_tag}"
compose=(docker compose --env-file .env -f "${compose_file}")

echo "Validating deployment configuration"
"${compose[@]}" config --quiet

echo "Pulling ${API_IMAGE}"
"${compose[@]}" pull api migrate

echo "Starting PostgreSQL and Redis"
"${compose[@]}" up -d postgres redis

echo "Applying database migrations"
"${compose[@]}" run --rm migrate

previous_image="$("${compose[@]}" ps -q api | xargs -r docker inspect --format '{{.Config.Image}}' 2>/dev/null || true)"

echo "Starting API"
"${compose[@]}" up -d --no-deps api

container_id="$("${compose[@]}" ps -q api)"
if [[ -z "${container_id}" ]]; then
    echo "API container was not created" >&2
    exit 1
fi

for _ in {1..30}; do
    health="$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}missing{{end}}' "${container_id}")"
    case "${health}" in
        healthy)
            printf '%s\n' "${API_IMAGE}" > .deployed-image
            echo "Deployment completed: ${API_IMAGE}"
            exit 0
            ;;
        unhealthy)
            break
            ;;
    esac
    sleep 3
done

echo "API did not become healthy. Recent logs:" >&2
"${compose[@]}" logs --tail=100 api >&2
if [[ -n "${previous_image}" ]]; then
    echo "Previous image was ${previous_image}" >&2
    echo "Inspect migration compatibility before rolling back." >&2
fi
exit 1
