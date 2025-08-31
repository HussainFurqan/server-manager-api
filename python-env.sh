python -m venv .venv

source .venv/bin/activate

python -m pip install -U pip

pip install "fastapi==0.115.*" "uvicorn[standard]==0.30.*" \
            "psycopg[binary,pool]==3.2.*" "pydantic-settings==2.4.*" "python-dotenv==1.0.*"

pip install "ruff==0.5.*" "pylint==3.2.*"
