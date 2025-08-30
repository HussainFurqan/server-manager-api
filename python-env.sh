# in the project folder
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# upgrade pip
python -m pip install -U pip

# install runtime deps (no ORM!)
pip install "fastapi==0.115.*" "uvicorn[standard]==0.30.*" \
            "psycopg[binary,pool]==3.2.*" "pydantic-settings==2.4.*" "python-dotenv==1.0.*"

# (optional) linters, style
pip install "ruff==0.5.*" "pylint==3.2.*"
