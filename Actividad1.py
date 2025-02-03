import simpy
import random
import matplotlib.pyplot as plt
import seaborn as sns

TIEMPO_LLEGADA_PROMEDIO = 5 
TIEMPO_CARGA_PROMEDIO = 7 
TIEMPO_SIMULACION = 600   
NUM_SURTIDORES = 2    


class EstacionServicio:
    def __init__(self, env, num_surtidores):
        self.env = env
        self.surtidores = simpy.Resource(env, num_surtidores)
        self.tiempos_espera = []
        self.tiempos_carga = []

    def cargar_combustible(self, vehiculo):
        tiempo_carga = random.expovariate(1.0 / TIEMPO_CARGA_PROMEDIO)
        self.tiempos_carga.append(tiempo_carga)
        yield self.env.timeout(tiempo_carga)
        print(f"Vehiculo {vehiculo} termino de cargar combustible a los {self.env.now:.2f} minutos.")

    def agregar_tiempo_espera(self, tiempo):
        self.tiempos_espera.append(tiempo)


def llegada_vehiculos(env, estacion):
    vehiculo_id = 0
    while True:
        tiempo_llegada = random.expovariate(1.0 / TIEMPO_LLEGADA_PROMEDIO)
        yield env.timeout(tiempo_llegada)

        vehiculo_id += 1
        print(f"Vehiculo {vehiculo_id} llega a la estacion a los {env.now:.2f} minutos.")
        
        tiempo_llegada = env.now

        with estacion.surtidores.request() as surtidor:
            yield surtidor
            tiempo_espera = env.now - tiempo_llegada
            estacion.agregar_tiempo_espera(tiempo_espera)
            print(f"Vehiculo {vehiculo_id} comienza a cargar combustible tras esperar {tiempo_espera:.2f} minutos.")
            yield env.process(estacion.cargar_combustible(vehiculo_id))


env = simpy.Environment()
estacion = EstacionServicio(env, NUM_SURTIDORES)

env.process(llegada_vehiculos(env, estacion))

env.run(until=TIEMPO_SIMULACION)

tiempo_promedio_espera = sum(estacion.tiempos_espera) / len(estacion.tiempos_espera)
utilizacion_surtidores = sum(estacion.tiempos_carga) / (NUM_SURTIDORES * TIEMPO_SIMULACION) * 100

print("\nResultados de la simulacion:")
print(f"Tiempo promedio de espera: {tiempo_promedio_espera:.2f} minutos.")
print(f"Numero total de Vehiculo atendidos: {len(estacion.tiempos_espera)}.")
print(f"Utilizacion de los surtidores: {utilizacion_surtidores:.2f}%.")
if utilizacion_surtidores > 80:
    print("Se recomienda incrementar la capacidad de la estacion.")
else:
    print("La capacidad de la estacion es adecuada.")

plt.figure(figsize=(12, 8))

plt.subplot(1, 2, 1)
sns.histplot(estacion.tiempos_carga, kde=True, color='orange')
plt.title("Distribucion del Tiempo de Carga")
plt.xlabel("Tiempo de Carga (minutos)")
plt.ylabel("Frecuencia")

plt.subplot(1, 2, 2)
plt.plot(range(len(estacion.tiempos_espera)), estacion.tiempos_espera, marker='o', color='green')
plt.title("Tiempos de Espera por Vehiculo")
plt.xlabel("Vehiculo")
plt.ylabel("Tiempo de Espera (minutos)")

plt.tight_layout()
plt.show()
