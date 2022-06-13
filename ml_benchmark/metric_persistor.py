import time
import docker
import psycopg2
import sqlalchemy
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float


class MetricPersistor:

    port = 5432
    user = "root"
    password = "1234"
    db = "benchmark_metrics"
    connection_string = f"postgresql://{user}:{password}@localhost:{port}/{db}"

    def __init__(self, connection_string: str = None) -> None:

        if connection_string:
            self.connection_string = connection_string
        self.client = docker.from_env()
        self.client.containers.run(
            "postgres:14.1", detach=True,
            environment=[f"POSTGRES_PASSWORD={self.password}", f"POSTGRES_DB={self.db}", f"POSTGRES_USER={self.user}"],
            ports={f'{self.port}/tcp': 5432},
            name="postgres",
            remove=True)
        container = self.client.containers.get("postgres")
        # checks if db is up
        while "accepting connections" not in container.exec_run("pg_isready").output.decode():
            time.sleep(2)
        print("DB-Container Running")
        self.conn = self._connect_to_postgres(self.connection_string)
        self.create_metrics_tables()

    def stop_database(self):
        container = self.client.containers.get("postgres")
        container.stop()

    def _connect_to_postgres(self, connection_string):
        try:
            self.conn = create_engine(connection_string, echo=True)
        except psycopg2.Error:
            raise ConnectionError("Could not establish a Database Connection to the postgres DB.")

    def create_metrics_tables(self):
        self.meta = MetaData()
        self.latency = Table(
            "latency", self.meta,
            Column("function_name", String)

        )

    def create_latency_table(self):
        pass



if __name__ == "__main__":
    print(MetricPersistor.connection_string)
