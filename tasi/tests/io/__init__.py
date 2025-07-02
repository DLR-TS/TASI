# %%
import os

os.chdir("..")

os.environ["TASIORM_USER"] = "scenimini_appl_user"
os.environ["TASIORM_PASSWORD"] = (
    "256BBF6E1E60034364F73ED9F045B1000A976EAABA2CB8789BE3EA85DB965B9D"
)

os.environ["TASIORM_HOSTNAME"] = "ts-pgc-proxy01-bs.intra.dlr.de"
os.environ["TASIORM_PORT"] = "6432"
os.environ["TASIORM_DATABASE"] = "scenimini"
os.environ["TASIORM_CONTEXT"] = "testing"

# %%
from tasi.io.env import DEFAULT_DATABASE_SETTINGS

engine = DEFAULT_DATABASE_SETTINGS.create_engine()
# %%
engine
# %%
from tasi.io.orm import MODELS, create_tables, drop_tables

create_tables(engine)
# %%
drop_tables(engine)
# %%
