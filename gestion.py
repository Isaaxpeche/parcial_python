# control_tareas.py
# Sistema de control de tareas - CLI


from typing import List, Dict, Tuple, Optional

# --- Constantes / tuplas para estados ---
ESTADOS: Tuple[str, ...] = ("pendiente", "en progreso", "completada")

# --- Datos en memoria ---
usuarios: List[Dict] = []   # cada usuario es un dict con campos y lista de tareas 
tareas: List[Dict] = []    # cada tarea es un dict con referencia al id_usuario

# --- Helpers / Utilidades ---
def generar_id(prefijo: str, coleccion: List[Dict]) -> str:
    """Generar id simple único: prefijo + numero."""
    return f"{prefijo}{len(coleccion) + 1}"

def encontrar_usuario_por_id(uid: str) -> Optional[Dict]:
    for u in usuarios:
        if u["id"] == uid:
            return u
    return None

def encontrar_tarea_por_id(tid: str) -> Optional[Dict]:
    for t in tareas:
        if t["id"] == tid:
            return t
    return None

# --- CRUD Usuarios ---
def crear_usuario():
    nombre = input("Nombre: ").strip()
    identificacion = input("Identificación: ").strip()
    contacto = input("Contacto: ").strip()
    rol = input("Rol: ").strip()
    uid = generar_id("U", usuarios)
    usuario = {
        "id": uid,
        "nombre": nombre,
        "identificacion": identificacion,
        "contacto": contacto,
        "rol": rol,
        "tareas": []  # lista de ids de tareas -> estructura anidada
    }
    usuarios.append(usuario)
    print(f"Usuario creado con id: {uid}")

def listar_usuarios():
    if not usuarios:
        print("No hay usuarios registrados.")
        return
    for u in usuarios:
        print(f"{u['id']} | {u['nombre']} | ID:{u['identificacion']} | {u['rol']} | tareas:{len(u['tareas'])}")

def consultar_usuario():
    uid = input("Ingrese id de usuario a consultar: ").strip()
    u = encontrar_usuario_por_id(uid)
    if not u:
        print("Usuario no encontrado.")
        return
    print("Detalles del usuario:")
    for k, v in u.items():
        if k == "tareas":
            print(f"  tareas ({len(v)}): {v}")
        else:
            print(f"  {k}: {v}")

def actualizar_usuario():
    uid = input("Id de usuario a actualizar: ").strip()
    u = encontrar_usuario_por_id(uid)
    if not u:
        print("Usuario no existe.")
        return
    print("Dejar en blanco para mantener valor actual.")
    nombre = input(f"Nombre ({u['nombre']}): ").strip() or u['nombre']
    contacto = input(f"Contacto ({u['contacto']}): ").strip() or u['contacto']
    rol = input(f"Rol ({u['rol']}): ").strip() or u['rol']
    u.update({"nombre": nombre, "contacto": contacto, "rol": rol})
    print("Usuario actualizado.")

def eliminar_usuario():
    uid = input("Id de usuario a eliminar: ").strip()
    u = encontrar_usuario_por_id(uid)
    if not u:
        print("Usuario no existe.")
        return
    # integridad: eliminar o reasignar tareas asociadas. Aquí optamos por eliminar las tareas vinculadas.
    tareas_a_eliminar = list(u["tareas"])  # copia
    for tid in tareas_a_eliminar:
        t = encontrar_tarea_por_id(tid)
        if t:
            tareas.remove(t)
    usuarios.remove(u)
    print(f"Usuario {uid} y sus {len(tareas_a_eliminar)} tareas relacionadas eliminadas.")

# --- CRUD Tareas ---
def crear_tarea():
    titulo = input("Título tarea: ").strip()
    descripcion = input("Descripción: ").strip()
    # validar usuario antes de asignar
    listar_usuarios()
    uid = input("Asignar a (id usuario) - deje vacío si sin asignar: ").strip()
    if uid:
        u = encontrar_usuario_por_id(uid)
        if not u:
            print("Usuario no encontrado. No se puede asignar la tarea.")
            return
    else:
        u = None
    tid = generar_id("T", tareas)
    estado = ESTADOS[0]  # pendiente por defecto
    tarea = {
        "id": tid,
        "titulo": titulo,
        "descripcion": descripcion,
        "asignado_a": u["id"] if u else None,
        "estado": estado
    }
    tareas.append(tarea)
    if u:
        u["tareas"].append(tid)  # estructura anidada: usuario contiene lista de ids de tareas
    print(f"Tarea creada con id: {tid}")

def listar_tareas(filtro_estado: Optional[str] = None):
    lista = tareas
    if filtro_estado:
        lista = [t for t in tareas if t["estado"] == filtro_estado]
    if not lista:
        print("No hay tareas para mostrar.")
        return
    for t in lista:
        print(f"{t['id']} | {t['titulo']} | {t['estado']} | asignado:{t['asignado_a']}")

def consultar_tarea():
    tid = input("Id tarea a consultar: ").strip()
    t = encontrar_tarea_por_id(tid)
    if not t:
        print("Tarea no encontrada.")
        return
    print("Detalles de la tarea:")
    for k, v in t.items():
        print(f"  {k}: {v}")

def actualizar_tarea():
    tid = input("Id tarea a actualizar: ").strip()
    t = encontrar_tarea_por_id(tid)
    if not t:
        print("Tarea no existe.")
        return
    print("Dejar en blanco para mantener valor actual.")
    titulo = input(f"Título ({t['titulo']}): ").strip() or t['titulo']
    descripcion = input(f"Descripción ({t['descripcion']}): ").strip() or t['descripcion']
    print("Estados válidos:", ESTADOS)
    estado = input(f"Estado ({t['estado']}): ").strip() or t['estado']
    if estado not in ESTADOS:
        print("Estado inválido. Manteniendo actual.")
        estado = t['estado']
    # reasignación: validar usuario existe
    listar_usuarios()
    asignado = input(f"Asignar a (id usuario) actualmente {t['asignado_a']} - dejar vacío para no cambiar: ").strip()
    if asignado:
        u_nuevo = encontrar_usuario_por_id(asignado)
        if not u_nuevo:
            print("Usuario nuevo no existe. No se cambia la asignación.")
            asignado = t['asignado_a']
        else:
            # actualizar listas en usuarios: quitar de viejo, agregar a nuevo
            if t['asignado_a']:
                u_viejo = encontrar_usuario_por_id(t['asignado_a'])
                if u_viejo and tid in u_viejo['tareas']:
                    u_viejo['tareas'].remove(tid)
            u_nuevo['tareas'].append(tid)
    else:
        asignado = t['asignado_a']
    t.update({"titulo": titulo, "descripcion": descripcion, "estado": estado, "asignado_a": asignado})
    print("Tarea actualizada.")

def eliminar_tarea():
    tid = input("Id tarea a eliminar: ").strip()
    t = encontrar_tarea_por_id(tid)
    if not t:
        print("Tarea no existe.")
        return
    # integridad: remover referencia desde usuario
    if t['asignado_a']:
        u = encontrar_usuario_por_id(t['asignado_a'])
        if u and tid in u['tareas']:
            u['tareas'].remove(tid)
    tareas.remove(t)
    print("Tarea eliminada.")

# --- Reportes ---
def reporte_tareas_por_usuario():
    listar_usuarios()
    uid = input("Id usuario para reporte: ").strip()
    u = encontrar_usuario_por_id(uid)
    if not u:
        print("Usuario no existe.")
        return
    if not u['tareas']:
        print("Usuario no tiene tareas.")
        return
    print(f"Tareas de {u['nombre']}:")
    for tid in u['tareas']:
        t = encontrar_tarea_por_id(tid)
        if t:
            print(f"  {t['id']} | {t['titulo']} | {t['estado']}")

def reporte_resumen_por_estado():
    resumen = {estado: 0 for estado in ESTADOS}
    for t in tareas:
        resumen[t['estado']] += 1
    print("Resumen tareas por estado:")
    for estado, cantidad in resumen.items():
        print(f"  {estado}: {cantidad}")

# --- Menús ---
def menu_usuario():
    opciones = {
        "1": ("Crear usuario", crear_usuario),
        "2": ("Listar usuarios", listar_usuarios),
        "3": ("Consultar usuario", consultar_usuario),
        "4": ("Actualizar usuario", actualizar_usuario),
        "5": ("Eliminar usuario", eliminar_usuario),
        "0": ("Volver", None)
    }
    while True:
        print("\n--- Menú Usuario ---")
        for k, v in opciones.items():
            print(f"{k}. {v[0]}")
        opt = input("Opción: ").strip()
        if opt == "0":
            break
        accion = opciones.get(opt)
        if accion:
            accion[1]()
        else:
            print("Opción inválida.")

def menu_tareas():
    opciones = {
        "1": ("Crear tarea", crear_tarea),
        "2": ("Listar todas las tareas", listar_tareas),
        "3": ("Listar tareas por estado", lambda: listar_tareas(filtro_estado=input("Estado filtro: ").strip())),
        "4": ("Consultar tarea", consultar_tarea),
        "5": ("Actualizar tarea", actualizar_tarea),
        "6": ("Eliminar tarea", eliminar_tarea),
        "7": ("Reporte tareas por usuario", reporte_tareas_por_usuario),
        "8": ("Resumen tareas por estado", reporte_resumen_por_estado),
        "0": ("Volver", None)
    }
    while True:
        print("\n--- Menú Tareas ---")
        for k, v in opciones.items():
            print(f"{k}. {v[0]}")
        opt = input("Opción: ").strip()
        if opt == "0":
            break
        accion = opciones.get(opt)
        if accion:
            accion[1]()
        else:
            print("Opción inválida.")

def main_menu():
    opciones = {
        "1": ("Menú Usuario", menu_usuario),
        "2": ("Menú Tareas", menu_tareas),
        "0": ("Salir", None)
    }
    while True:
        print("\n=== Sistema de Control de Tareas ===")
        for k, v in opciones.items():
            print(f"{k}. {v[0]}")
        opt = input("Seleccione opción: ").strip()
        if opt == "0":
            print("Saliendo... chao.")
            break
        accion = opciones.get(opt)
        if accion:
            accion[1]()
        else:
            print("Opción inválida.")

if __name__ == "__main__":
 
    usuarios.append({"id": "U1", "nombre": "Ana", "identificacion": "1001", "contacto": "ana@ej", "rol": "dev", "tareas": []})
    usuarios.append({"id": "U2", "nombre": "Luis", "identificacion": "1002", "contacto": "luis@ej", "rol": "qa", "tareas": []})


    main_menu()

