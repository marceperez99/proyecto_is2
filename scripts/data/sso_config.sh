CLIENT_ID=$1
SECRET=$2
echo "[{
    \"model\": \"sites.site\",
    \"pk\": 1,
    \"fields\": {\"domain\": \"localhost:8000\", \"name\": \"localhost\"}},
  {
    \"model\": \"socialaccount.socialapp\",
    \"pk\": 1,
    \"fields\": {
      \"provider\": \"google\",
      \"name\": \"gapi\",
      \"client_id\": \"$CLIENT_ID\",
      \"secret\": \"$SECRET\",
      \"key\": \"\",
      \"sites\": [1]
    }
  }
]"