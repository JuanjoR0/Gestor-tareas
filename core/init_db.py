import random
from datetime import date, timedelta
from django.contrib.auth.models import User
from core.models import Board, TaskList, Task, TAGS_CHOICES


def initialize_data():
    # Si ya existen usuarios, no vuelvas a crear datos
    if User.objects.exists():
        return

    # --- Crear superusuario ---
    superadmin = User.objects.create_superuser(
        username="Juanjo", password="usuario1234", email="juanjo@example.com"
    )

    # --- Crear usuarios normales ---
    usuarios = []
    for nombre in ["David", "Maria", "Reyes", "Sonia"]:
        user = User.objects.create_user(
            username=nombre,
            password="usuario1234",
            email=f"{nombre.lower()}@example.com"
        )
        usuarios.append(user)

    # --- Crear tablero ---
    tablero = Board.objects.create(name="Tareas", owner=superadmin)
    tablero.members.add(superadmin, *usuarios)

    # --- Crear listas ---
    nombres_listas = ["Pendientes", "En ello", "Por corregir", "Finalizadas"]
    listas = []
    for i, nombre in enumerate(nombres_listas, start=1):
        listas.append(TaskList.objects.create(name=nombre, board=tablero, position=i))

    # --- Opciones ---
    prioridades = ["low", "medium", "high"]
    titulos = [
        "Revisar documentación",
        "Corregir errores",
        "Desarrollar nueva funcionalidad",
        "Reunión con el equipo",
        "Diseño de la interfaz",
        "Optimizar rendimiento",
        "Escribir tests",
        "Actualizar dependencias",
        "Preparar presentación",
        "Configurar despliegue",
    ]

    descripciones = [
        "Tarea generada automáticamente como ejemplo.",
        "Esta tarea es parte del flujo de pruebas inicial.",
        "Pendiente de revisión y asignación final.",
        "Ejemplo de descripción detallada de la tarea.",
    ]

    etiquetas = [tag[0] for tag in TAGS_CHOICES]

    # --- Crear 3 tareas en cada lista ---
    for lista in listas:
        for _ in range(3):
            titulo = random.choice(titulos)
            descripcion = random.choice(descripciones)
            prioridad = random.choice(prioridades)

            # Fecha aleatoria: pasada, próxima o lejana
            dias_offset = random.choice([-10, -2, 5, 15, 45])
            fecha = date.today() + timedelta(days=dias_offset)

            # Etiquetas aleatorias (1 o 2)
            tags = ",".join(random.sample(etiquetas, random.randint(1, 2)))

            # Crear tarea
            task = Task.objects.create(
                title=titulo,
                description=descripcion,
                task_list=lista,
                due_date=fecha,
                tags=tags,
                priority=prioridad,
                position=random.randint(0, 10)
            )

            # Asignar 1 o 2 usuarios al azar
            asignados = random.sample(usuarios, random.randint(1, 2))
            task.assigned_to.set(asignados)

    print("✅ Datos iniciales creados: superadmin, usuarios, tablero, listas y tareas.")
