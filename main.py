import tkinter
from tkinter import messagebox
import tkintermapview
from geopy.geocoders import Nominatim
import csv
from tkinter import Menu

import numpy as np
import random

from geopy.distance import geodesic
import pandas as pd

import os

csv_file_path = 'location_info.csv'

# create tkinter window
root_tk = tkinter.Tk()
root_tk.geometry(f"{1000}x{700}")
root_tk.title("Rota Hesapla")

menubar = Menu(root_tk)
root_tk.config(menu=menubar)

# create a menu
file_menu = Menu(menubar)
help_menu = Menu(menubar)
def openHelp():
    help_window = tkinter.Toplevel(root_tk)
    help_window.title("Nasıl Çalışır")

    # Yeni pencere içeriği
    label = tkinter.Label(help_window, text="Nasıl Çalışır?")
    label2 = tkinter.Label(help_window, text="1- İstenilen koordinatı seçmek için sağ click yapılıp Koordinat Seç seçilir.")
    label3 = tkinter.Label(help_window, text="2- 20 Adet koordinat seçildikten sonra 'Parametreler' kısmına tıklanır ")
    label4 = tkinter.Label(help_window, text="3- Parametrelerin hepsi doldurulup 'Rotayı Hesapla Butonuna tıklayınız.' ")
    label5 = tkinter.Label(help_window, text="4- Duraklar sırayla belirtilmiştir . Sıraya göre rotayı takip edebilirsiniz ")
    
    label6 = tkinter.Label(help_window, text="Uyarılar!",fg="red")
    label7 = tkinter.Label(help_window, text="Bu proje amacında yalnızca sınırlar Balıkesir ili olarak tanımlanmıştır",fg="red")
    label8 = tkinter.Label(help_window, text="Bu proje amacında yalnızca 20 Koordinat girilebilir olarak tanımlanmıştır",fg="red")
    label9 = tkinter.Label(help_window, text="Başka bir nokta seçin uyarı verirse haritaya yakınlaşıp uzaklaşarak tekrar deneyiniz",fg="red")
    
    label10 = tkinter.Label(help_window, text="Güvenli Sürüşler Dileriz :)",fg="green")

    label.pack(padx=20, pady=20)
    label2.pack(padx=20, pady=20)
    label3.pack(padx=20, pady=20)
    label4.pack(padx=20, pady=20)
    label5.pack(padx=20, pady=20)
    label6.pack(padx=20, pady=20)
    label7.pack(padx=20, pady=20)
    label8.pack(padx=20, pady=20)
    label9.pack(padx=20, pady=20)
    label10.pack(padx=20, pady=20)
    
    

def openEdit():
    global entry_population,generations_entry,mutation_entry,cross_entry

    edit_window = tkinter.Toplevel(root_tk)
    edit_window.title("Parametre Düzenle")
    edit_window.geometry(f"{300}x{200}")

    population_label = tkinter.Label(edit_window,text='Population:')
    entry_population = tkinter.Entry(edit_window)

    generations_label = tkinter.Label(edit_window,text='Generations:')
    generations_entry = tkinter.Entry(edit_window)

    mutation_label = tkinter.Label(edit_window,text='Mutation:')
    mutation_entry = tkinter.Entry(edit_window)

    cross_label = tkinter.Label(edit_window,text='Cross-Over:')
    cross_entry = tkinter.Entry(edit_window)

    buton = tkinter.Button(edit_window, text="Rotayı hesapla",command=result)

    population_label.grid(row=0, column=0, padx=10, pady=5, sticky="e")
    entry_population.grid(row=0, column=1, pady=5)

    generations_label.grid(row=1, column=0, padx=10, pady=5, sticky="e")
    generations_entry.grid(row=1, column=1, pady=5)

    mutation_label.grid(row=2, column=0, padx=10, pady=5, sticky="e")
    mutation_entry.grid(row=2, column=1, pady=5)

    cross_label.grid(row=3, column=0, padx=10, pady=5, sticky="e")
    cross_entry.grid(row=3, column=1, pady=5)

    buton.grid(row=4, column=0, columnspan=2, pady=10)

# add a menu item to the menu
file_menu.add_command(
    label='Parametreleri Düzenle',
    command=openEdit
)
file_menu.add_command(
    label='Çıkış',
    command=root_tk.destroy
)


help_menu.add_command(
    label='Nasıl Çalışır',
    command=openHelp
)
# Başlangıç popülasyonunu oluştur
def generate_individual():
    return list(range(len(drive_distances)))
# Fitness fonksiyonu: Sürüş mesafelerini topla
def fitness(individual):
    total_distance = 0
    for i in range(len(individual) - 1):
        total_distance += drive_distances[individual[i]][individual[i + 1]]
    return -total_distance  # Minimizasyon problemleri için negatif fitness
# Seçilim
def select_parents(population):
    parents = random.sample(population, k=2)
    return parents
# Çaprazlama
def crossover(parent1, parent2 ,rate):
    child1 = parent1[:rate] + [gene for gene in parent2 if gene not in parent1[:rate]]
    child2 = parent2[:rate] + [gene for gene in parent1 if gene not in parent2[:rate]]
    return child1, child2

# Mutasyon
def mutate(individual):
    if random.random() < mutation_rate:
        idx1, idx2 = random.sample(range(len(individual)), k=2)
        individual[idx1], individual[idx2] = individual[idx2], individual[idx1]
    return individual
def draw_route(rot):
    map_widget.delete_all_marker()
    df =pd.read_csv(csv_file_path)
    a=1
    for i in rot:
        text = f"{a}.Durak"
        
        new_marker = map_widget.set_marker(df.loc[i]['lat'], df.loc[i]['lon'], text=text)
        a+=1
    os.remove(csv_file_path)
    os.remove("mesafeler.csv")
def result():
    global drive_distances,mutation_rate
    if(len(entry_population.get())!=0 and len(generations_entry.get())!=0 and len(mutation_entry.get())!=0 and len(mutation_entry.get())!=0 ):

        df = pd.read_csv(csv_file_path)# CSV dosyasını oku
        # Koordinatları içeren bir liste oluştur
        coordinates = list(zip(df['lat'], df['lon']))
        # Mesafe matrisini oluştur
        distance_matrix = []
        for coord1 in coordinates:
            distances = []
            for coord2 in coordinates:
                distance = geodesic(coord1, coord2).kilometers
                distances.append(distance)
            distance_matrix.append(distances)
        with open('mesafeler.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(distance_matrix)
        
        
        drive_distances = distance_matrix
        # Genetik algoritma parametreleri
        population_size = int(entry_population.get())
        generations = int(generations_entry.get())
        mutation_rate = float(mutation_entry.get())
        cros_rate = int(cross_entry.get())
        population = [generate_individual() for _ in range(population_size)]
        
        # Genetik algoritma
        for generation in range(generations):
        # Fitness değerlerini hesapla
            fitness_values = [fitness(individual) for individual in population]

            # En iyi bireyleri seç
            elite_idx = np.argmax(fitness_values)
            elite = population[elite_idx]

            # Yeni popülasyonu oluştur
            new_population = [elite]

            while len(new_population) < population_size:
                parent1, parent2 = select_parents(population)
                child1, child2 = crossover(parent1, parent2,cros_rate)
                child1 = mutate(child1)
                child2 = mutate(child2)
                new_population.extend([child1, child2])

            # Yeni popülasyonu güncelle
            population = new_population

                # Sonuçları ekrana yazdır
        best_individual = max(population, key=fitness)
        best_fitness = fitness(best_individual)
        print("En iyi rotasyon:", best_individual)
        print("Toplam mesafe:", -best_fitness)
        draw_route(best_individual)
        text=f"Toplam mesafe:{ best_fitness*-1}"
        messagebox.showinfo('Rota Başarıyla oluşturuldu',text)
    else:
        messagebox.showerror('Error', 'Lütfen Parametre Giriniz!')
# add the File menu to the menubar
menubar.add_cascade(label="Parametreler",menu=file_menu)
menubar.add_cascade(label="Yardım",menu=help_menu)

i=1

map_widget = tkintermapview.TkinterMapView(root_tk, width=1000, height=700, corner_radius=0)
map_widget.pack(fill="both", expand=True)
geolocator = Nominatim(user_agent="final")

def add_marker_event(coords):
    global i
    if i <21:
        try:
            adres =geolocator.reverse(coords).raw['address']
            city = adres['province']
            konum =adres['town']

            if city == 'Balıkesir':
                
                new_marker = map_widget.set_marker(coords[0], coords[1], text=i)
                new_data = {'id':i, 'konum':konum , 'lat':coords[0], 'lon':coords[1]}
                with open(csv_file_path, mode='a', newline='' ,encoding='utf-8') as file:
                    writer = csv.DictWriter(file, fieldnames=['id', 'konum','lat','lon'])

            # Eğer dosya boşsa, başlık satırını yaz
                    if file.tell() == 0:
                        writer.writeheader()

            # Veriyi yaz
                    writer.writerow(new_data)
                i+=1
            else:
                messagebox.showerror('Error', 'Lütfen Balıkesir ilinden bir nokta seçiniz!')
        except KeyError:
            messagebox.showerror('Error', 'Lütfen başka bir nokta seçiniz!')
    else:
        messagebox.showerror('Error', 'Daha fazla seçim yapamazsınız!')
        
map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
map_widget.set_position(39.645728405060666, 27.890223091026026)  # Başlangıç konumu Altıeylül , Balıkesir seçildi
map_widget.set_zoom(10)
polygon_1 = map_widget.set_polygon([
                    (39.3192 ,26.6924),
                    ( 39.3834,27.6539 ),
                    (39.1650385 ,28.1030298),
                    (39.0905876, 28.4573900),
                    (39.2967369 ,28.7114511),
                    (39.4076936, 28.9449345),
                    (39.599532, 28.992330),
                    (39.686246, 28.728658),
                    (39.745402, 28.723165),
                    (39.760184, 28.525411),
                    (40.164373, 28.118917),
                    (40.394863, 28.228780),
                    (40.500415, 27.950689),
                    (40.518687, 27.707616),
                    (40.485794, 27.687017),
                    (40.302761, 27.512609),
                    (39.778128, 27.430212),
                    (39.778128, 27.430212),
                    (39.658763, 27.295629),
                    (39.762295, 26.909734),
                    (39.680962, 26.702367),
                    (39.680962, 26.702367),
                    (39.559311, 26.652929)
        ],
                                   # fill_color=None,
                                    outline_color="red",
                                   # border_width=12,
                                   #command=add_marker_event,
                                   name="switzerland_polygon")




    

map_widget.add_right_click_menu_command(label="Koordinat Seç",
                                        command=add_marker_event,
                                        pass_coords=True)
root_tk.mainloop()