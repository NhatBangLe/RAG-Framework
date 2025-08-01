# AI Agent Configuration Toolkit

AI Agent Configuration Toolkit is a part of Creating AI Agent Framework from my bachelor's graduation thesis.

Creating AI Agent Framework includes two parts:

- AI Agent Configuration Toolkit.
- AI Agent Service.

The toolkit helps to create configuration files for configuring AI Agent Service.

## Installation

Use the Poetry package manager [poetry](https://python-poetry.org/docs/basic-usage/#installing-dependencies) to install
dependencies.

At the folder that contains a `pyproject.toml` file, use this command:

```bash
poetry install --no-root
```

Required environment variables:

- `MONGODB_URI`: MongoDB host. Example: mongodb://admin:admin@localhost:27017/admin
- `MONGODB_DATABASE`: MongoDB database name.

Additional environment variables (optional):

- `LOG_LEVEL`: Logging level, default `INFO`. Available values: INFO, WARNING, DEBUG.
- `CACHE_DIR`= Path to a cache folder, default in `/app/cache` folder.
- `LOCAL_FILE_DIR`: Path to local saved files folder, default in `/app/local` folder.
- `DOWNLOAD_SECURE_KEY`: A secret key to generate tokens for downloading files, default
  `your-super-secret-key-change-in-production`.

## Usage

1. Run MongoDB service.
2. Run the server, use the below command:

```bash
fastapi run ./src/main.py
```

Check the API documentation at `/docs` to see endpoints.

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)