import sqlite3
from config import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from datetime import datetime
from pytz import timezone    
import time


class DB_Map():
    def __init__(self, database):
        self.database = database
    
    def create_user_table(self):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS users_cities (
                                user_id INTEGER,
                                city_id TEXT,
                                FOREIGN KEY(city_id) REFERENCES cities(id)
                            )''')
            conn.commit()

    def add_city(self,user_id, city_name ):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM cities WHERE city=?", (city_name,))
            city_data = cursor.fetchone()
            if city_data:
                city_id = city_data[0]  
                conn.execute('INSERT INTO users_cities VALUES (?, ?)', (user_id, city_id))
                conn.commit()
                return 1
            else:
                return 0

            
    def select_cities(self, user_id):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute('''SELECT cities.city, cities.country
                            FROM users_cities  
                            JOIN cities ON users_cities.city_id = cities.id
                            WHERE users_cities.user_id = ?''', (user_id,))

            cities = [row[0] for row in cursor.fetchall()]
            return cities


    def get_coordinates(self, city_name):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute('''SELECT lat, lng
                            FROM cities  
                            WHERE city = ?''', (city_name,))
            coordinates = cursor.fetchone()
            return coordinates

    def create_grapf(self, color, cities, path='city.png'):
        plt.figure(figsize=(11, 8.5))
        ax = plt.axes(projection=ccrs.PlateCarree())
        ax.add_feature(cfeature.BORDERS, linewidth=0.5, edgecolor='blue')
        ax.stock_img()

        for city in cities:
            coordinates = self.get_coordinates(city)

            if coordinates:
                lat, lng = coordinates
                plt.plot([lng], [lat], color=color, linewidth=10, marker='o', ms = 6, transform=ccrs.Geodetic())
                plt.text(lng + 1.5, lat + 6, city, fontsize=10, fontweight='bold', horizontalalignment='left', transform=ccrs.Geodetic())
        
        plt.savefig(path)
        plt.close()

        
    def draw_distance(self, city1, city2):
        city1_coords = self.get_coordinates(city1)
        city2_coords = self.get_coordinates(city2)
        fig, ax = plt.subplots(subplot_kw={'projection': ccrs.PlateCarree()})
        ax.stock_img()
        plt.plot([city1_coords[1], city2_coords[1]], [city1_coords[0], city2_coords[0]], color='red', linewidth=1.5, marker='o', ms = 6 , transform=ccrs.Geodetic())
        plt.plot([city1_coords[1], city2_coords[1]], [city1_coords[0], city2_coords[0]], color='gray', linestyle='--', linewidth=1, transform=ccrs.PlateCarree())
        plt.text(city1_coords[1] + 3, city1_coords[0] + 12, city1, horizontalalignment='left', transform=ccrs.Geodetic())
        plt.text(city2_coords[1] + 3, city2_coords[0] + 12, city2, horizontalalignment='left', transform=ccrs.Geodetic())
        plt.savefig('distance_map.png')
        plt.close()


if __name__=="__main__":
    
    m = DB_Map(DATABASE)
    m.create_user_table()