from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import data_model
import env
# import mysql.connector


def model_setter(src_model: object, des_model: object):
    props = list(filter(lambda o: o[0] != '_', dir(src_model)))
    for prop in props:
        if prop == 'sid':
            continue
        setattr(des_model, prop, getattr(src_model, prop))
    return des_model


class Session(object):
    def __init__(self, connect_str=env.connect_str):
        engine = create_engine(connect_str)
        self.__session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)()

    def db_writer(self, model):
        self.__session.add(model)
        self.__session.commit()

    def db_list_writer(self, models):
        self.__session.bulk_save_objects(models)
        self.__session.commit()

    def close_session(self):
        self.__session.close()

    def query_all(self, model_name):
        return self.__session.query(model_name).all()
