import re
import sys

def ejecutar_codigo(codigo):
    entorno = {}
    salida = []

    lineas = codigo.strip().split('\n')
    for num_linea, linea in enumerate(lineas, start=1):
        linea = linea.strip()

        if not linea or linea.startswith('#'):
            continue  # Ignorar líneas vacías o comentarios

        try:
            if linea.startswith('chaj '):
                # Declaración de variable
                partes = linea.replace(';', '').split('=')
                identificador = partes[0].replace('chaj', '').strip()
                valor = eval(partes[1], {}, entorno)
                entorno[identificador] = valor

            elif linea.startswith('qex '):
                # Impresión
                contenido = re.findall(r'"(.*?)"', linea)
                if contenido:
                    salida.append(contenido[0])
                else:
                    # Puede ser una variable
                    var = linea.replace('qex', '').replace(';', '').strip()
                    salida.append(str(entorno.get(var, f"[Error: {var} no definida]")))

            elif '=' in linea:
                # Asignación simple
                partes = linea.replace(';', '').split('=')
                identificador = partes[0].strip()
                valor = eval(partes[1], {}, entorno)
                entorno[identificador] = valor

            elif 'toq' in linea or 'b\'ah' in linea:
                salida.append("[Advertencia: estructuras condicionales aún no se interpretan en este modo básico]")

            else:
                salida.append(f"[Error en línea {num_linea}]: Sintaxis no reconocida.")

        except Exception as e:
            salida.append(f"[Error en línea {num_linea}]: {str(e)}")

    return '\n'.join(salida)


if __name__ == "__main__":
    if sys.stdin.isatty():
        print("Introduce el código Tonayu por stdin.")
        sys.exit(0)

    codigo_fuente = sys.stdin.read()
    resultado = ejecutar_codigo(codigo_fuente)
    print(resultado)
