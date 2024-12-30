# Se crea función para obtener los discos por parte del usuario
def get_disks():
    number_disk = int(input("Enter the number of disks: "))
    disks = []
    for i in range(1, number_disk + 1):
        tuple = ()
        size = int(input(f"Enter the size of disk {i}: "))
        color = input(f"Enter the color of disk {i}: ")
        tuple = (size, color)
        disks.append(tuple)
    return disks

# Se calculan los movimientos considerando las restricciones de color y tamaño
def calculate_moves(n, disks, source="A", target="C", auxiliary="B", moves=None):
    # Inicializar la lista de movimientos si no se proporciona
    if moves is None:
        moves = []

    # Verificar si los discos tienen colores consecutivos iguales
    for i in range(1, n):
        if disks[i][1] == disks[i - 1][1]:
            return -1  # Restricción de colores violada

    # Se retorna si no hay discos
    if n == 0:
        return moves

    # Paso 1: Mueve los primeros n-1 discos de origen a auxiliar
    calculate_moves(n - 1, disks[:-1], source, auxiliary, target, moves)

    # Paso 2: Mueve el disco más grande (último en la lista) de origen a destino
    moves.append((disks[-1][0], source, target))

    # Paso 3: Mueve los n-1 discos de auxiliar a destino
    calculate_moves(n - 1, disks[:-1], auxiliary, target, source, moves)

    return moves

#Se define funcion main para ejecutar el programa
def main():
    #Se obtienen los discos
    disks = get_disks()
    moves = calculate_moves(len(disks), disks)
    print(moves)
    
# Se ejecuta la funcion main
if __name__ == "__main__":
    main()