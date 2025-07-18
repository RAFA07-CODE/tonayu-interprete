import time
from datetime import datetime
from collections import Counter
import json
import sys
import traceback
import re

# Configuración de encoding para Windows
sys.stdin.reconfigure(encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# ==================== TOKENS Y LEXER ====================
TOKENS_NAHUATL = {
    # Alfabeto (IDs 1-22)
    'a': {'nahuatl': 'ātl (agua)', 'id': 1, 'tipo': 'Letra'},
    'b': {'nahuatl': 'be (adaptado)', 'id': 2, 'tipo': 'Letra'},
    'ch': {'nahuatl': 'chīchīltik (rojo brillante)', 'id': 3, 'tipo': 'Letra'},
    'e': {'nahuatl': 'ēhecatl (viento)', 'id': 4, 'tipo': 'Letra'},
    'i': {'nahuatl': 'īztli (obsidiana)', 'id': 5, 'tipo': 'Letra'},
    'j': {'nahuatl': 'xōchitl (flor)', 'id': 6, 'tipo': 'Letra'},
    'k': {'nahuatl': 'kalli (casa)', 'id': 7, 'tipo': 'Letra'},
    'l': {'nahuatl': 'lolli (rodar)', 'id': 8, 'tipo': 'Letra'},
    'm': {'nahuatl': 'metl (maguey)', 'id': 9, 'tipo': 'Letra'},
    'n': {'nahuatl': 'nāhui (cuatro)', 'id': 10, 'tipo': 'Letra'},
    'o': {'nahuatl': 'ōlli (hule)', 'id': 11, 'tipo': 'Letra'},
    'p': {'nahuatl': 'pilli (noble)', 'id': 12, 'tipo': 'Letra'},
    'q': {'nahuatl': 'quema (sí)', 'id': 13, 'tipo': 'Letra'},
    'r': {'nahuatl': 'tepetl (cerro)', 'id': 14, 'tipo': 'Letra'},
    's': {'nahuatl': 'cuīcatl (canto)', 'id': 15, 'tipo': 'Letra'},
    't': {'nahuatl': 'tlācatl (persona)', 'id': 16, 'tipo': 'Letra'},
    'u': {'nahuatl': 'uh (adaptado)', 'id': 17, 'tipo': 'Letra'},
    'w': {'nahuatl': 'huēyi (grande)', 'id': 18, 'tipo': 'Letra'},
    'x': {'nahuatl': 'xīcotl (avispa)', 'id': 19, 'tipo': 'Letra'},
    'y': {'nahuatl': 'yōllotl (corazón)', 'id': 20, 'tipo': 'Letra'},
    'z': {'nahuatl': 'zacatl (pasto)', 'id': 21, 'tipo': 'Letra'},
    "'": {'nahuatl': 'corte glotal', 'id': 22, 'tipo': 'Delimitador'},

    # Operadores (IDs 100-111)
    '+': {'nahuatl': 'tlen mochīhua (suma)', 'id': 100, 'tipo': 'Operador'},
    '-': {'nahuatl': 'tlāzotl (resta)', 'id': 101, 'tipo': 'Operador'},
    '*': {'nahuatl': 'chīchīltik yāotl (multiplicación)', 'id': 102, 'tipo': 'Operador'},
    '/': {'nahuatl': 'nextepōllotl (división)', 'id': 103, 'tipo': 'Operador'},
    '%': {'nahuatl': 'centēchīuh (módulo)', 'id': 104, 'tipo': 'Operador'},
    '=': {'nahuatl': 'tlen tlatskanī (asignación)', 'id': 105, 'tipo': 'Operador'},
    '==': {'nahuatl': 'tlatskanī tōkāitl (igualdad)', 'id': 106, 'tipo': 'Operador'},
    '!=': {'nahuatl': 'amochīhuanī (desigualdad)', 'id': 107, 'tipo': 'Operador'},
    '<': {'nahuatl': 'tepōztli ichan (menor que)', 'id': 108, 'tipo': 'Operador'},
    '>': {'nahuatl': 'tepōztli īhuān (mayor que)', 'id': 109, 'tipo': 'Operador'},
    '<=': {'nahuatl': 'tepōztli ichan o igual', 'id': 110, 'tipo': 'Operador'},
    '>=': {'nahuatl': 'tepōztli īhuān o igual', 'id': 111, 'tipo': 'Operador'},

    # Palabras reservadas (IDs 300-312)
    'chaj': {'nahuatl': 'tlatskanī', 'id': 300, 'tipo': 'Keyword'},
    'qex': {'nahuatl': 'tlahcuiloa', 'id': 301, 'tipo': 'Keyword'},
    'toj': {'nahuatl': 'zān (if)', 'id': 302, 'tipo': 'Keyword'},
    'muk': {'nahuatl': 'nechicoliztli huehcāuh (while/for)', 'id': 303, 'tipo': 'Keyword'},
    "b'ah": {'nahuatl': 'calli tlatskayotl', 'id': 304, 'tipo': 'Keyword'},
    "nik": {'nahuatl': 'mopanō', 'id': 305, 'tipo': 'Keyword'},
    "pek'": {'nahuatl': 'tēchpoua', 'id': 306, 'tipo': 'Keyword'},
    'chok': {'nahuatl': 'huīca', 'id': 307, 'tipo': 'Keyword'},
    "utz'": {'nahuatl': 'tēchmaca', 'id': 308, 'tipo': 'Keyword'},
    'naq': {'nahuatl': 'tlachiyalistli', 'id': 309, 'tipo': 'Keyword'},
    'ja': {'nahuatl': 'quēmah (true)', 'id': 310, 'tipo': 'Literal'},
    'ma': {'nahuatl': 'ahmo quēmah (false)', 'id': 311, 'tipo': 'Literal'},
    'ahmo': {'nahuatl': 'ahmo cualcān (None)', 'id': 312, 'tipo': 'Literal'},

    # Tipos de datos (IDs 400-405)
    'loq': {'nahuatl': 'cadena (string)', 'id': 400, 'tipo': 'Type'},
    'matlaktli': {'nahuatl': 'entero (int)', 'id': 401, 'tipo': 'Type'},
    'ompa': {'nahuatl': 'decimal (float)', 'id': 402, 'tipo': 'Type'},
    'tlāzi': {'nahuatl': 'tupla (tuple)', 'id': 403, 'tipo': 'Type'},
    'tlāltikpak': {'nahuatl': 'conjunto (set)', 'id': 404, 'tipo': 'Type'},
    'cuixcoatli': {'nahuatl': 'diccionario (dict)', 'id': 405, 'tipo': 'Type'}
}

PATTERNS = [
    # Comentarios (se ignoran)
    (r'#.*', None),
    (r"'''.*?'''", None, re.DOTALL),
    
    # Palabras reservadas (las que contienen comillas simples están corregidas aquí 👇)
    (r'\bchaj\b', {'tipo': 'DECLARACION', 'id': 300}),
    (r'\bqex\b', {'tipo': 'IMPRIMIR', 'id': 301}),
    (r'\btoj\b', {'tipo': 'CONDICIONAL', 'id': 302}),
    (r'\bmuk\b', {'tipo': 'BUCLE', 'id': 303}),
    (r"b'ah", {'tipo': 'INICIO_BLOQUE', 'id': 304}),     # 👈 corregido
    (r"nik'", {'tipo': 'FIN_BLOQUE', 'id': 305}),        # 👈 corregido
    (r"pek'", {'tipo': 'DEF_FUNCION', 'id': 306}),       # 👈 corregido
    (r'\bchok\b', {'tipo': 'LLAMADA_FUNCION', 'id': 307}),
    (r"utz'", {'tipo': 'RETORNO', 'id': 308}),           # 👈 corregido
    (r'\bnaq\b', {'tipo': 'COMPARACION', 'id': 309}),
    (r'\bja\b', {'tipo': 'VERDADERO', 'id': 310}),
    (r'\bma\b', {'tipo': 'FALSO', 'id': 311}),
    (r'\bahmo\b', {'tipo': 'NONE', 'id': 312}),
    
    # Tipos de datos
    (r'\bloq\b', {'tipo': 'TIPO_CADENA', 'id': 400}),
    (r'\bmatlaktli\b', {'tipo': 'TIPO_ENTERO', 'id': 401}),
    (r'\bompa\b', {'tipo': 'TIPO_DECIMAL', 'id': 402}),
    (r'\btlāzi\b', {'tipo': 'TIPO_TUPLA', 'id': 403}),
    (r'\btlāltikpak\b', {'tipo': 'TIPO_CONJUNTO', 'id': 404}),
    (r'\bcuixcoatli\b', {'tipo': 'TIPO_DICCIONARIO', 'id': 405}),
    
    # Literales
    (r'\b\d+\.?\d*\b', {'tipo': 'NUMERO', 'id': 500}),
    (r'"[^"]*"', {'tipo': 'CADENA', 'id': 501}),

    # Operadores (ordenados correctamente)
    (r'\bnaq\b', {'tipo': 'IGUAL_QUE', 'id': 106}),               # palabra reservada alternativa
    (r'==', {'tipo': 'IGUAL_QUE', 'id': 106}),                   # debe ir antes que '='
    (r'!=', {'tipo': 'DIFERENTE_QUE', 'id': 107}),               # antes que '!'
    (r'<=', {'tipo': 'MENOR_IGUAL_QUE', 'id': 110}),             # antes que '<'
    (r'>=', {'tipo': 'MAYOR_IGUAL_QUE', 'id': 111}),             # antes que '>'
    (r'=', {'tipo': 'ASIGNACION', 'id': 105}),
    (r'<', {'tipo': 'MENOR_QUE', 'id': 108}),
    (r'>', {'tipo': 'MAYOR_QUE', 'id': 109}),
    (r'\+', {'tipo': 'SUMA', 'id': 100}),
    (r'-', {'tipo': 'RESTA', 'id': 101}),
    (r'\*', {'tipo': 'MULTIPLICACION', 'id': 102}),
    (r'/', {'tipo': 'DIVISION', 'id': 103}),
    (r'%', {'tipo': 'MODULO', 'id': 104}),
    (r'\(', {'tipo': 'PARENTESIS_IZQ', 'id': 200}),
    (r'\)', {'tipo': 'PARENTESIS_DER', 'id': 201}),
    (r'\{', {'tipo': 'LLAVE_IZQ', 'id': 202}),
    (r'\}', {'tipo': 'LLAVE_DER', 'id': 203}),
    (r'\[', {'tipo': 'CORCHETE_IZQ', 'id': 204}),
    (r'\]', {'tipo': 'CORCHETE_DER', 'id': 205}),
    (r',', {'tipo': 'COMA', 'id': 206}),
    (r';', {'tipo': 'PUNTO_COMA', 'id': 207}),
    (r':', {'tipo': 'DOS_PUNTOS', 'id': 208}),


    # Identificadores
    (r'\b[a-z][a-z0-9\']*\b', {'tipo': 'IDENTIFICADOR', 'id': 700}),

    # Espacios
    (r'\s+', None)
]

def analisis_lexico(codigo):
    """Analizador léxico completo para Tonayu"""
    tokens = []
    errores = []
    linea = 1
    posicion = 0
    
    # Preprocesamiento: eliminar comentarios multilínea
    codigo = re.sub(r"'''.*?'''", "", codigo, flags=re.DOTALL)
    
    while posicion < len(codigo):
        match = None
        for pattern_data in PATTERNS:
            if len(pattern_data) == 2:
                pattern, token_info = pattern_data
                flags = 0
            else:
                pattern, token_info, flags = pattern_data
                
            try:
                regex = re.compile(pattern, flags)
                match = regex.match(codigo, posicion)
                if match:
                    valor = match.group(0)
                    if token_info:  # Si no es un token a ignorar
                        # Obtener significado náhuatl
                        nahuatl_info = TOKENS_NAHUATL.get(valor, {})
                        nahuatl = nahuatl_info.get('nahuatl', '—')
                        
                        # Construir token
                        token = {
                            'id': token_info['id'],
                            'token': valor,
                            'tipo': token_info['tipo'],
                            'linea': linea,
                            'posicion': match.start(),
                            'nahuatl': nahuatl
                        }
                        
                        # Manejo especial para literales
                        if token_info['tipo'] == 'NUMERO':
                            token['valor'] = float(valor) if '.' in valor else int(valor)
                        elif token_info['tipo'] == 'CADENA':
                            token['valor'] = valor[1:-1]  # Eliminar comillas
                        
                        tokens.append(token)
                    
                    # Manejo de saltos de línea
                    saltos = valor.count('\n')
                    if saltos > 0:
                        linea += saltos
                    
                    posicion = match.end()
                    break
            except Exception as e:
                errores.append({
                    'tipo': 'Error léxico',
                    'mensaje': f"Error procesando patrón {pattern}: {str(e)}",
                    'linea': linea,
                    'posicion': posicion
                })
        
        if not match:
            # Carácter no reconocido
            errores.append({
                'tipo': 'Error léxico',
                'mensaje': f"Carácter no reconocido: '{codigo[posicion]}'",
                'linea': linea,
                'posicion': posicion,
                'caracter': codigo[posicion]
            })
            posicion += 1
    
    return tokens, errores

        
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.posicion = 0
        self.errores = []

    def parse(self):
        """Analiza el programa completo"""
        try:
            programa = []
            while not self._esta_al_final():
                programa.append(self._parse_sentencia())
            return programa
        except Exception as e:
            self.errores.append({
                'tipo': 'Error sintáctico',
                'mensaje': str(e),
                'linea': self._token_actual().get('linea', 1)
            })
            return []

    def _parse_sentencia(self):
        """Parsear una sentencia individual"""
        token = self._token_actual()

        if token['tipo'] == 'DECLARACION':
            return self._parse_declaracion()
        elif token['tipo'] == 'IMPRIMIR':
            return self._parse_imprimir()
        elif token['tipo'] == 'CONDICIONAL':
            return self._parse_condicional()
        elif token['tipo'] == 'BUCLE':
            return self._parse_bucle()
        elif token['tipo'] == 'DEF_FUNCION':
            return self._parse_funcion()
        elif token['tipo'] == 'RETORNO':
            return self._parse_retorno()
        elif token['tipo'] == 'LLAMADA_FUNCION':
            return self._parse_llamada_funcion()
        elif token['tipo'] == 'IDENTIFICADOR' and self._siguiente_es('ASIGNACION'):
            return self._parse_asignacion()
        else:
            raise SyntaxError(f"Sentencia no válida: {token['token']}")

    def _parse_declaracion(self):
        """chaj ID (: tipo)? = valor ;  o solo chaj ID : tipo ;"""
        self._consumir('DECLARACION', "Esperaba 'chaj'")
        identificador = self._consumir('IDENTIFICADOR', "Esperaba nombre de variable")

        tipo = None
        if self._coincide('DOS_PUNTOS'):
            self._avanzar()
            tipo_token = self._consumir('IDENTIFICADOR', "Esperaba tipo de dato")
            tipo = tipo_token['token']

        if self._coincide('ASIGNACION'):
            self._avanzar()
            expresion = self._parse_expresion()
            self._consumir('PUNTO_COMA', "Esperaba ';'")
            return {
                'tipo': 'Declaracion',
                'identificador': identificador['token'],
                'tipo_dato': tipo,
                'expresion': expresion,
                'linea': identificador['linea']
            }
        else:
            self._consumir('PUNTO_COMA', "Esperaba ';'")
            return {
                'tipo': 'Declaracion',
                'identificador': identificador['token'],
                'tipo_dato': tipo,
                'expresion': None,
                'linea': identificador['linea']
            }

    def _parse_asignacion(self):
        """x = expresion;"""
        identificador = self._consumir('IDENTIFICADOR', "Esperaba nombre de variable")
        self._consumir('ASIGNACION', "Esperaba '='")
        expresion = self._parse_expresion()
        self._consumir('PUNTO_COMA', "Esperaba ';'")
        return {
            'tipo': 'Asignacion',
            'identificador': identificador['token'],
            'expresion': expresion,
            'linea': identificador['linea']
        }

    def _parse_imprimir(self):
        """qex "texto";"""
        self._consumir('IMPRIMIR', "Esperaba 'qex'")
        expresion = self._parse_expresion()
        self._consumir('PUNTO_COMA', "Esperaba ';'")
        return {
            'tipo': 'Imprimir',
            'expresion': expresion,
            'linea': self._token_anterior()['linea']
        }

    def _parse_condicional(self):
        """toj condicion b'ah ... nik' (amo ika b'ah ... nik')?"""
        self._consumir('CONDICIONAL', "Esperaba 'toj'")
        condicion = self._parse_expresion()
        bloque_si = self._parse_bloque()

        bloque_no = None
        if self._coincide('IDENTIFICADOR') and self._token_actual()['token'] == 'amo':
            self._avanzar()  # consume 'amo'
            if self._coincide('IDENTIFICADOR') and self._token_actual()['token'] == 'ika':
                self._avanzar()  # consume 'ika'
                bloque_no = self._parse_bloque()
            else:
                raise SyntaxError("Esperaba 'ika' después de 'amo' para el bloque else")

        return {
            'tipo': 'Condicional',
            'condicion': condicion,
            'bloque_si': bloque_si,
            'bloque_no': bloque_no,
            'linea': self._token_anterior()['linea']
        }


    def _parse_funcion(self):
        """pek' nombre(parametros) b'ah ... nik'"""
        self._consumir('DEF_FUNCION', "Esperaba 'pek''")
        nombre = self._consumir('IDENTIFICADOR', "Esperaba nombre de función")
        self._consumir('PARENTESIS_IZQ', "Esperaba '('")

        parametros = []
        if not self._coincide('PARENTESIS_DER'):
            while True:
                param = self._consumir('IDENTIFICADOR', "Esperaba parámetro")
                parametros.append(param['token'])
                if not self._coincide('COMA'):
                    break
                self._avanzar()

        self._consumir('PARENTESIS_DER', "Esperaba ')'")
        bloque = self._parse_bloque()
        return {
            'tipo': 'Funcion',
            'nombre': nombre['token'],
            'parametros': parametros,
            'bloque': bloque,
            'linea': nombre['linea']
        }

    def _parse_llamada_funcion(self):
        """chok nombre(parametros);"""
        self._consumir('LLAMADA_FUNCION', "Esperaba 'chok'")
        nombre = self._consumir('IDENTIFICADOR', "Esperaba nombre de función")
        self._consumir('PARENTESIS_IZQ', "Esperaba '('")

        argumentos = []
        if not self._coincide('PARENTESIS_DER'):
            while True:
                argumentos.append(self._parse_expresion())
                if not self._coincide('COMA'):
                    break
                self._avanzar()

        self._consumir('PARENTESIS_DER', "Esperaba ')'")
        self._consumir('PUNTO_COMA', "Esperaba ';'")
        return {
            'tipo': 'LlamadaFuncion',
            'nombre': nombre['token'],
            'argumentos': argumentos,
            'linea': nombre['linea']
        }

    def _parse_retorno(self):
        """utz' valor;"""
        self._consumir('RETORNO', "Esperaba 'utz''")
        if self._coincide('PUNTO_COMA'):
            self._avanzar()
            return {'tipo': 'Retorno', 'valor': None}
        else:
            valor = self._parse_expresion()
            self._consumir('PUNTO_COMA', "Esperaba ';'")
            return {'tipo': 'Retorno', 'valor': valor}

    def _parse_bucle(self):
        """muk (...) {for} o muk expr {while}"""
        self._consumir('BUCLE', "Esperaba 'muk'")

        if self._coincide('PARENTESIS_IZQ'):
            self._avanzar()
            if self._coincide('DECLARACION'):
                inicio = self._parse_declaracion()
            elif self._coincide('IDENTIFICADOR'):
                inicio = self._parse_asignacion()
            else:
                raise SyntaxError("Esperaba declaración o asignación en bucle for")

            condicion = self._parse_expresion()
            self._consumir('PUNTO_COMA', "Esperaba ';' tras condición")
            paso = self._parse_asignacion()
            self._consumir('PARENTESIS_DER', "Esperaba ')' tras encabezado de bucle")
            bloque = self._parse_bloque()

            return {
                'tipo': 'BucleFor',
                'inicio': inicio,
                'condicion': condicion,
                'paso': paso,
                'bloque': bloque
            }

        else:
            condicion = self._parse_expresion()
            bloque = self._parse_bloque()
            return {
                'tipo': 'BucleWhile',
                'condicion': condicion,
                'bloque': bloque
            }

    def _parse_bloque(self):
        """Parsea un bloque de instrucciones encerrado entre b'ah y nik'."""
        token = self._token_actual()
        if token['tipo'] != 'INICIO_BLOQUE':
            raise SyntaxError(f"Esperaba 'b'ah' para inicio de bloque, pero se encontró '{token['token']}' en línea {token.get('linea', '?')}.")

        self._consumir('INICIO_BLOQUE', "Esperaba 'b'ah'")
        instrucciones = []

        while not self._coincide('FIN_BLOQUE') and not self._esta_al_final():
            instrucciones.append(self._parse_sentencia())

        if not self._coincide('FIN_BLOQUE'):
            raise SyntaxError(f"Bloque sin cerrar correctamente. Faltó 'nik'' antes del final.")

        self._consumir('FIN_BLOQUE', "Esperaba 'nik''")
        return instrucciones



    def _parse_expresion(self):
        """Expresión general"""
        return self._parse_logica()
    
    def _parse_logica(self):
        """ExprComp (īhuān | nozo) ExprComp"""
        expr = self._parse_igualdad()
        
        while self._coincide('IDENTIFICADOR') and self._token_actual()['token'] in ('īhuān', 'nozo'):
            operador = self._avanzar()
            derecha = self._parse_igualdad()
            expr = {
                'tipo': 'ExpresionBinaria',
                'izquierda': expr,
                'operador': operador['token'],
                'derecha': derecha,
                'linea': operador['linea']
            }
        
        return expr

    def _parse_igualdad(self):
        expr = self._parse_comparacion()
        while self._verifica('IGUAL_QUE', 'DIFERENTE_QUE'):
            operador = self._token_anterior()
            derecha = self._parse_comparacion()
            expr = {
                'tipo': 'ExpresionBinaria',
                'izquierda': expr,
                'operador': operador['token'],
                'derecha': derecha,
                'linea': operador['linea']
            }
        return expr

    def _parse_comparacion(self):
        expr = self._parse_aritmetica()
        while self._verifica('MENOR_QUE', 'MAYOR_QUE', 'MENOR_IGUAL_QUE', 'MAYOR_IGUAL_QUE'):
            operador = self._token_anterior()
            derecha = self._parse_aritmetica()
            expr = {
                'tipo': 'ExpresionBinaria',
                'izquierda': expr,
                'operador': operador['token'],
                'derecha': derecha,
                'linea': operador['linea']
            }
        return expr

    def _parse_aritmetica(self):
        expr = self._parse_termino()
        while self._verifica('SUMA', 'RESTA'):
            operador = self._token_anterior()
            derecha = self._parse_termino()
            expr = {
                'tipo': 'ExpresionBinaria',
                'izquierda': expr,
                'operador': operador['token'],
                'derecha': derecha,
                'linea': operador['linea']
            }
        return expr

    def _parse_termino(self):
        expr = self._parse_factor()
        while self._verifica('MULTIPLICACION', 'DIVISION', 'MODULO'):
            operador = self._token_anterior()
            derecha = self._parse_factor()
            expr = {
                'tipo': 'ExpresionBinaria',
                'izquierda': expr,
                'operador': operador['token'],
                'derecha': derecha,
                'linea': operador['linea']
            }
        return expr


    def _parse_factor(self):
        if self._coincide('RESTA'):
            operador = self._token_anterior()
            return {
                'tipo': 'ExpresionUnaria',
                'operador': operador['token'],
                'expresion': self._parse_factor(),
                'linea': operador['linea']
            }
        return self._parse_elemento()

    def _parse_elemento(self):
        """Analiza un elemento básico: identificador, literal, acceso, lista, tupla o diccionario."""
# Llamada a función como expresión: chok nombre(...)
        if self._coincide('LLAMADA_FUNCION'):
            self._avanzar()
            nombre = self._consumir('IDENTIFICADOR', "Esperaba nombre de función")
            self._consumir('PARENTESIS_IZQ', "Esperaba '('")

            argumentos = []
            if not self._coincide('PARENTESIS_DER'):
                while True:
                    argumentos.append(self._parse_expresion())
                    if not self._coincide('COMA'):
                        break
                    self._avanzar()

            self._consumir('PARENTESIS_DER', "Esperaba ')'")

            return {
                'tipo': 'LlamadaFuncion',
                'nombre': nombre['token'],
                'argumentos': argumentos,
                'linea': nombre['linea']
            }
        
        # Identificador + posibles accesos [i] o [i:j]
        if self._coincide('IDENTIFICADOR'):
            token = self._avanzar()
            base = {
                'tipo': 'Identificador',
                'nombre': token['token'],
                'linea': token['linea']
            }

            # Accesos múltiples posibles
            while self._coincide('CORCHETE_IZQ'):
                self._avanzar()
                inicio = self._parse_expresion()

                if self._coincide('DOS_PUNTOS'):
                    self._avanzar()
                    fin = self._parse_expresion()
                    self._consumir('CORCHETE_DER', "Esperaba ']' tras acceso con rango")
                    base = {
                        'tipo': 'Slice',
                        'estructura': base,
                        'inicio': inicio,
                        'fin': fin,
                        'linea': self._token_anterior()['linea']
                    }
                else:
                    self._consumir('CORCHETE_DER', "Esperaba ']'")
                    base = {
                        'tipo': 'Acceso',
                        'estructura': base,
                        'indice': inicio,
                        'linea': self._token_anterior()['linea']
                    }

            return base

        # Literales simples
        elif self._coincide('NUMERO', 'CADENA', 'VERDADERO', 'FALSO', 'NONE'):
            token = self._avanzar()
            return {
                'tipo': 'Literal',
                'valor': token.get('valor', token['token']),
                'linea': token['linea']
            }

        # Lista
        elif self._coincide('CORCHETE_IZQ'):
            self._avanzar()
            elementos = []
            if not self._coincide('CORCHETE_DER'):
                while True:
                    elementos.append(self._parse_expresion())
                    if not self._coincide('COMA'):
                        break
                    self._avanzar()
            self._consumir('CORCHETE_DER', "Esperaba ']'")
            return {
                'tipo': 'Lista',
                'elementos': elementos,
                'linea': self._token_anterior()['linea']
            }

        # Diccionario
        elif self._coincide('LLAVE_IZQ'):
            self._avanzar()
            elementos = []
            if not self._coincide('LLAVE_DER'):
                while True:
                    clave = self._parse_expresion()
                    self._consumir('DOS_PUNTOS', "Esperaba ':' en diccionario")
                    valor = self._parse_expresion()
                    elementos.append((clave, valor))
                    if not self._coincide('COMA'):
                        break
                    self._avanzar()
            self._consumir('LLAVE_DER', "Esperaba '}'")
            return {
                'tipo': 'Diccionario',
                'elementos': elementos,
                'linea': self._token_anterior()['linea']
            }

        # Tupla o expresión entre paréntesis
        elif self._coincide('PARENTESIS_IZQ'):
            self._avanzar()
            primer = self._parse_expresion()
            if self._coincide('COMA'):
                elementos = [primer]
                while self._coincide('COMA'):
                    self._avanzar()
                    elementos.append(self._parse_expresion())
                self._consumir('PARENTESIS_DER', "Esperaba ')'")
                return {
                    'tipo': 'Tupla',
                    'elementos': elementos,
                    'linea': self._token_anterior()['linea']
                }
            else:
                self._consumir('PARENTESIS_DER', "Esperaba ')'")
                return primer

        else:
            token = self._token_actual()
            raise SyntaxError(f"Elemento inesperado: {token['token']}")


    def _coincide(self, *tipos):
        """Revisa si el token actual coincide con alguno de los tipos dados."""
        if self._esta_al_final():
            return False
        return self.tokens[self.posicion]['tipo'] in tipos

    def _siguiente_es(self, tipo):
        return self.posicion + 1 < len(self.tokens) and self.tokens[self.posicion + 1]['tipo'] == tipo
    
    def _verifica(self, *tipos):
        """Verifica si el token actual coincide con alguno de los tipos dados y avanza si es así."""
        if self._esta_al_final():
            return False
        if self.tokens[self.posicion]['tipo'] in tipos:
            self._avanzar()
            return True
        return False

    def _consumir(self, tipo_esperado, mensaje_error):
        token = self._token_actual()
        if token['tipo'] != tipo_esperado:
            raise SyntaxError(f"{mensaje_error} en línea {token.get('linea', '?')} (se encontró '{token['token']}').")
        self.posicion += 1
        return token

    def _avanzar(self):
        if not self._esta_al_final():
            self.posicion += 1
        return self._token_anterior()

    def _token_actual(self):
        if self._esta_al_final():
            return {'tipo': 'EOF', 'token': 'EOF', 'linea': '?'}
        return self.tokens[self.posicion]


    def _token_anterior(self):
        return self.tokens[self.posicion - 1]

    def _esta_al_final(self):
        return self.posicion >= len(self.tokens)

class Grammar:
    def __init__(self):
        self.productions = {
            'programa': [['sentencia*']],
            'sentencia': [
                ['declaracion'],
                ['asignacion'],
                ['imprimir'],
                ['condicional'],
                ['bucle']
            ],
            'declaracion': [
                ["'chaj'", 'IDENTIFICADOR', "'='", 'expresion', "';'"]
            ],
            'imprimir': [
                ["'qex'", 'expresion', "';'"]
            ]
        }
    
    def validate_structure(self, tokens):
        """Validación básica de estructura gramatical"""
        return []  # Implementación simplificada
    
def generar_derivacion(arbol, nivel=0):
    """Devuelve la derivación textual del árbol sintáctico"""
    espacio = '  ' * nivel
    salida = ''
    
    for nodo in arbol:
        salida += espacio + f"{nodo['tipo']}\n"

        if nodo['tipo'] == 'Declaracion':
            salida += espacio + f"  ├── Identificador: {nodo['identificador']}\n"
            if nodo.get('tipo_dato'):
                salida += espacio + f"  ├── Tipo: {nodo['tipo_dato']}\n"
            if nodo.get('expresion'):
                salida += espacio + "  └── Valor:\n"
                salida += generate_single(nodo['expresion'], nivel + 2)

        elif nodo['tipo'] == 'Imprimir':
            salida += espacio + "  └── Expresión a imprimir:\n"
            salida += generar_derivacion([nodo['expresion']], nivel + 2)

        elif nodo['tipo'] == 'Condicional':
            salida += espacio + "  ├── Condición:\n"
            salida += generate_single(nodo['condicion'], nivel + 2)
            salida += espacio + "  ├── Bloque SI:\n"
            salida += generar_derivacion(nodo['bloque_si'], nivel + 2)
            if nodo.get('bloque_no'):
                salida += espacio + "  └── Bloque NO:\n"
                salida += generar_derivacion(nodo['bloque_no'], nivel + 2)

        elif nodo['tipo'] == 'BucleWhile':
            salida += espacio + "  ├── Condición:\n"
            salida += generate_single(nodo['condicion'], nivel + 2)
            salida += espacio + "  └── Bloque:\n"
            salida += generar_derivacion(nodo['bloque'], nivel + 2)

        elif nodo['tipo'] == 'BucleFor':
            salida += espacio + "  ├── Inicio:\n"
            salida += generar_derivacion([nodo['inicio']], nivel + 2)
            salida += espacio + "  ├── Condición:\n"
            salida += generate_single(nodo['condicion'], nivel + 2)
            salida += espacio + "  ├── Paso:\n"
            salida += generate_single(nodo['paso'], nivel + 2)
            salida += espacio + "  └── Bloque:\n"
            salida += generar_derivacion(nodo['bloque'], nivel + 2)

        elif nodo['tipo'] == 'Funcion':
            salida += espacio + f"  ├── Nombre: {nodo['nombre']}\n"
            salida += espacio + f"  ├── Parámetros: {', '.join(nodo['parametros'])}\n"
            salida += espacio + "  └── Bloque:\n"
            salida += generar_derivacion(nodo['bloque'], nivel + 2)

        elif nodo['tipo'] == 'LlamadaFuncion':
            salida += espacio + f"  ├── Nombre: {nodo['nombre']}\n"
            salida += espacio + f"  └── Argumentos:\n"
            salida += '\n'.join(generate_single(arg, nivel + 2) for arg in nodo['argumentos']) + '\n'

        elif nodo['tipo'] == 'Retorno':
            salida += espacio + "  └── Valor de retorno:\n"
            if nodo['valor']:
                salida += generate_single(nodo['valor'], nivel + 2)

    return salida

def generate_single(nodo, nivel=0):
    espacio = '  ' * nivel

    if nodo['tipo'] == 'Literal':
        valor = nodo['valor']
        if isinstance(valor, bool):
            tipo = "Booleano"
        elif isinstance(valor, (int, float)):
            tipo = "Número"
        elif isinstance(valor, str):
            tipo = "Texto"
        elif valor is None:
            tipo = "Nulo"
        else:
            tipo = "Literal"
        return espacio + f"{tipo}: {valor}\n"

    elif nodo['tipo'] == 'Identificador':
        return espacio + f"Identificador: {nodo['nombre']}\n"

    elif nodo['tipo'] == 'ExpresionBinaria':
        return (
            espacio + f"Expresión Binaria: {nodo['operador']}\n" +
            generate_single(nodo['izquierda'], nivel + 1) +
            generate_single(nodo['derecha'], nivel + 1)
        )

    elif nodo['tipo'] == 'Lista':
        return espacio + f"Lista: [{len(nodo['elementos'])} elementos]\n"

    elif nodo['tipo'] == 'Tupla':
        return espacio + f"Tupla: ({len(nodo['elementos'])} elementos)\n"

    elif nodo['tipo'] == 'Diccionario':
        return espacio + f"Diccionario: {{...}}\n"

    elif nodo['tipo'] == 'Acceso':
        return (
            espacio + f"Acceso a estructura:\n" +
            generate_single(nodo['estructura'], nivel + 1) +
            generate_single(nodo['indice'], nivel + 1)
        )

    return espacio + f"{nodo['tipo']} (sin representación)\n"


def ejecutar_arbol_sintactico(arbol):
    """Ejecuta el árbol sintáctico de Tonayu y genera salida."""
    salida = []
    entorno_global = {}

    def evaluar(nodo, entorno=None):
        if entorno is None:
            entorno = entorno_global

        tipo = nodo['tipo']

        if tipo == 'Declaracion':
            valor = evaluar(nodo['expresion']) if nodo['expresion'] else None
            entorno[nodo['identificador']] = valor
            return valor

        elif tipo == 'Asignacion':
            valor = evaluar(nodo['expresion'], entorno)
            entorno[nodo['identificador']] = valor
            return valor

        elif tipo == 'Imprimir':
            valor = evaluar(nodo['expresion'], entorno)
            if isinstance(valor, (list, dict)):
                import json
                valor = json.dumps(valor, ensure_ascii=False)
            salida.append(str(valor))
            return valor

        elif tipo == 'Condicional':
            if evaluar(nodo['condicion']):
                for sentencia in nodo['bloque_si']:
                    evaluar(sentencia)
            elif nodo['bloque_no']:
                for sentencia in nodo['bloque_no']:
                    evaluar(sentencia)
            return None

        elif tipo == 'BucleWhile':
            while evaluar(nodo['condicion'], entorno):
                for sentencia in nodo['bloque']:
                    resultado = evaluar(sentencia, entorno)
                    if isinstance(resultado, dict) and 'retorno' in resultado:
                        return resultado
            return None

        elif tipo == 'BucleFor':
            evaluar(nodo['inicio'], entorno)
            while evaluar(nodo['condicion'], entorno):
                for sentencia in nodo['bloque']:
                    resultado = evaluar(sentencia, entorno)
                    if isinstance(resultado, dict) and 'retorno' in resultado:
                        return resultado
                evaluar(nodo['paso'], entorno)
            return None

        elif tipo == 'Lista':
            return [evaluar(e) for e in nodo['elementos']]

        elif tipo == 'Tupla':
            return tuple(evaluar(e) for e in nodo['elementos'])

        elif tipo == 'Diccionario':
            return {evaluar(k): evaluar(v) for k, v in nodo['elementos']}

        elif tipo == 'Acceso':
            estructura = evaluar(nodo['estructura'])
            indice = evaluar(nodo['indice'])
            return estructura[indice]

        elif tipo == 'Slice':
            estructura = evaluar(nodo['estructura'])
            inicio = evaluar(nodo['inicio'])
            fin = evaluar(nodo['fin'])
            return estructura[inicio:fin]

        elif tipo == 'Funcion':
            entorno[nodo['nombre']] = nodo
            return None

        elif tipo == 'LlamadaFuncion':
            funcion = entorno.get(nodo['nombre'])
            if not funcion:
                raise NameError(f"Función no definida: {nodo['nombre']}")

            # Crear entorno local a partir de una copia del entorno global o actual
            nuevo_entorno = entorno.copy()

            # Validar cantidad de argumentos
            if len(nodo['argumentos']) != len(funcion['parametros']):
                raise ValueError(f"La función '{nodo['nombre']}' espera {len(funcion['parametros'])} argumento(s), pero recibió {len(nodo['argumentos'])}.")

            # Evaluar argumentos en entorno actual y almacenarlos en el entorno local
            for param, arg_expr in zip(funcion['parametros'], nodo['argumentos']):
                nuevo_entorno[param] = evaluar(arg_expr, entorno)

            # Ejecutar el cuerpo de la función en el entorno local
            for sentencia in funcion['bloque']:
                resultado = evaluar(sentencia, nuevo_entorno)
                if isinstance(resultado, dict) and 'retorno' in resultado:
                    return resultado['retorno']

            return None

        elif tipo == 'Retorno':
            valor = evaluar(nodo['valor'], entorno) if nodo['valor'] else None
            return {'retorno': valor}


        elif tipo == 'ExpresionBinaria':
            izquierda = evaluar(nodo['izquierda'], entorno)
            derecha = evaluar(nodo['derecha'], entorno)
            op = nodo['operador']

            if op == '+': return izquierda + derecha
            elif op == '-': return izquierda - derecha
            elif op == '*': return izquierda * derecha
            elif op == '/': return izquierda / derecha
            elif op == '%': return izquierda % derecha
            elif op in ('==', 'naq'): return izquierda == derecha
            elif op in ('!=', '≠'): return izquierda != derecha
            elif op == '<': return izquierda < derecha
            elif op == '>': return izquierda > derecha
            elif op == '<=': return izquierda <= derecha
            elif op == '>=': return izquierda >= derecha
            elif op == 'īhuān': return bool(izquierda) and bool(derecha)
            elif op == 'nozo': return bool(izquierda) or bool(derecha)
            else:
                raise ValueError(f"[Semántico] Operador no soportado: {op}")

        elif tipo == 'ExpresionUnaria':
            valor = evaluar(nodo['expresion'], entorno)
            if nodo['operador'] == '-':
                return -valor
            return valor

        elif tipo == 'Literal':
            return nodo['valor']

        elif tipo == 'Identificador':
            nombre = nodo['nombre']
            if nombre not in entorno:
                raise NameError(f"Variable no definida: {nombre}")
            return entorno[nombre]

        else:
            raise RuntimeError(f"Nodo no implementado: {tipo}")

    # ⏳ Ejecutar todas las sentencias del árbol sintáctico
    for sentencia in arbol:
        resultado = evaluar(sentencia)
        if isinstance(resultado, dict) and 'retorno' in resultado:
            break  # Detener si se retorna desde una función principal

    return salida

def main():
    start_time = time.time()
    
    try:
        if len(sys.argv) < 2:
            print(json.dumps({
                "error": "Se requiere archivo de entrada",
                "usage": "python interpreter.py <archivo.ton>",
                "ejemplo": "python interpreter.py programa.ton"
            }, ensure_ascii=False, indent=2))
            return

        # Leer código fuente del archivo
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            codigo = f.read().strip()

        if not codigo:
            print(json.dumps({
                "error": "El archivo está vacío",
                "solucion": "Verifique el contenido del archivo"
            }, ensure_ascii=False, indent=2))
            return

        # 1. Análisis léxico
        tokens, errores_lexico = analisis_lexico(codigo)

        # 2. Análisis sintáctico
        parser = Parser(tokens)
        arbol_sintactico = parser.parse()
        errores_sintactico = parser.errores

        # 3. Ejecución del árbol
        errores_semantico = []
        salida_consola = ""

        if not errores_lexico and not errores_sintactico:
            try:
                salida = ejecutar_arbol_sintactico(arbol_sintactico)
                salida_consola = "\n".join(salida)
            except Exception as e:
                errores_semantico.append({
                    'tipo': 'Semántico',
                    'mensaje': str(e),
                    'linea': traceback.extract_tb(e.__traceback__)[-1].lineno if hasattr(e, '__traceback__') else 0
                })

        # Resultado final
        resultado = {
            "estado": "éxito" if not any([errores_lexico, errores_sintactico, errores_semantico]) else "error",
            "console_output": salida_consola,
            "analisis": {
                "lexico": {
                    "tokens": tokens[:50],  # Muestra solo los primeros 50 tokens
                    "total_tokens": len(tokens),
                    "errores": errores_lexico
                },
                "sintactico": {
                    "errores": errores_sintactico
                },
                "semantico": {
                    "errores": errores_semantico
                }
            },
            "metadata": {
                "tiempo_ejecucion": time.time() - start_time,
                "version": "Tonayu 1.0",
                "fecha": datetime.now().isoformat()
            }
        }

        # Agregar derivación si no hubo errores críticos
        if arbol_sintactico:
            derivacion = generar_derivacion(arbol_sintactico)
            resultado["derivacion"] = derivacion

        # Mostrar resultado en consola
        print(json.dumps(resultado, ensure_ascii=False, indent=2))

    except Exception as e:
        error_data = {
            "error": "Error crítico",
            "mensaje": str(e),
            "traceback": traceback.format_exc()
        }
        print(json.dumps(error_data, ensure_ascii=False, indent=2))
        sys.exit(1)

if __name__ == "__main__":
    main()