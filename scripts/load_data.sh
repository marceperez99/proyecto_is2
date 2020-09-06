TEMP_DIR=$(mktemp -d)
GOOGLE_OAUTH_CLIENT_ID=$2
GOOGLE_OAUTH_SECRET_KEY=$3
SSO_KEYS="$TEMP_DIR/google_keys.json"

scripts/data/sso_config.sh "$GOOGLE_OAUTH_CLIENT_ID" "$GOOGLE_OAUTH_SECRET_KEY" > "$SSO_KEYS"

# Se cargan los datos del OAUTH
cat "$SSO_KEYS"
python manage.py loaddata "$SSO_KEYS"
rm "$SSO_KEYS"
# Se crea el super usuario
python manage.py shell < "scripts/create_admin.py"

# Se carga datos de prueba
python manage.py loaddata scripts/data/data.json