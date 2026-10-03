#!/usr/bin/env bash
python -c "from backend.app.database import Base, engine; from backend.app import models; Base.metadata.create_all(bind=engine); print('db initialized')"
