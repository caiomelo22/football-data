import math
import os
import numpy as np
import mysql.connector


class MySQLService:
    def __init__(self):
        self.host = os.getenv("DB_HOST")
        self.user = os.getenv("DB_USER")
        self.password = os.getenv("DB_PASSWORD")
        self.database = os.getenv("DB_DATABASE")
        self.conn = None
        self.cursor = None
        self.connect()

    def connect(self):
        try:
            self.conn = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
            )
            self.cursor = self.conn.cursor()
            print("Connected to MySQL database")
        except mysql.connector.Error as e:
            print(f"Error connecting to MySQL database: {e}")
            raise

    def create_table(self, table_name, columns):
        try:
            query = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)})"
            self.cursor.execute(query)
            self.conn.commit()
            print(f"Table '{table_name}' created successfully.")
        except mysql.connector.Error as e:
            print(f"Error creating table: {e}")
            self.conn.rollback()

    def create_table_from_df(self, table_name, df):
        try:
            columns = []

            # Mapping data types for table creation
            type_mapping = {
                "int64": "INT",
                "float64": "FLOAT",
                "datetime64[ns]": "DATETIME",
                "object": "VARCHAR(255)",
            }

            # Iterate over DataFrame columns to determine data types for table creation
            for col, dtype in df.dtypes.items():
                col_type = type_mapping.get(str(dtype), "VARCHAR(255)")
                columns.append(f"{col} {col_type}")

            # Create the table
            self.create_table(table_name=table_name, columns=columns)
        except Exception as e:
            print(f"Error creating table: {e}")

    def insert_data(self, table_name, data):
        try:
            columns = ", ".join(data.keys())
            values = ", ".join(["%s"] * len(data))
            query = f"INSERT INTO {table_name} ({columns}) VALUES ({values})"
            self.cursor.execute(query, list(data.values()))
            self.conn.commit()
            print("Data inserted successfully.")
        except mysql.connector.Error as e:
            print(f"Error inserting data: {e}")
            self.conn.rollback()

    def convert_nans_to_none(self, data_list):
        clean_list = []

        for row in data_list:
            clean_row = {}
            
            for k, v in row.items():
                if isinstance(v, float) and math.isnan(v):
                    clean_row[k] = None
                else:
                    clean_row[k] = v

            clean_list.append(clean_row)

        return clean_list

    def insert_multiple_rows(self, table_name, data_list):
        try:
            data_list = self.convert_nans_to_none(data_list)
            columns = data_list[0].keys()
            values = [tuple(row.values()) for row in data_list]
            
            if table_name == "matches":
                # Assuming 'id' is the unique key for the 'matches' table
                query = f"""
                    INSERT INTO {table_name} ({', '.join(columns)})
                    VALUES ({', '.join(['%s'] * len(columns))})
                    ON DUPLICATE KEY UPDATE 
                        home_odds = VALUES(home_odds),
                        away_odds = VALUES(away_odds),
                        draw_odds = VALUES(draw_odds)
                """
            else:
                query = f"INSERT IGNORE INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(['%s'] * len(columns))})"
            
            self.cursor.executemany(query, values)
            self.conn.commit()
            print("Multiple rows inserted/updated successfully.")
        except mysql.connector.Error as e:
            print(f"Error inserting/updating multiple rows: {e}")
            self.conn.rollback()


    def close(self):
        if self.conn and self.conn.is_connected():
            self.cursor.close()
            self.conn.close()
            print("Connection to MySQL database closed.")
