## Troubleshooting

### Issue: DAG shows "Import Error" or mount paths fail

**Solution:** Make sure you've created and configured the `.env` file with correct paths.
```bash
cd airflow
cp .env.example .env
# Edit .env with your actual paths
```

### Issue: Network "airflow-network" not found

**Solution:** Create the network manually:
```bash
docker network create airflow-network
```

### Issue: Permission denied when writing outputs

**Solution (Linux/Mac):** 
```bash
chmod -R 777 helical-model/outputs
```

**Solution (Windows):** Make sure Docker has access to the drive in Docker Desktop settings.

### Issue: Container metrics not showing in Grafana

**Solution:** 
1. Trigger the DAG at least once
2. Wait 30 seconds after execution
3. Refresh Grafana dashboard