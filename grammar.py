# grammar.py - Implementación completa de la gramática Tonayu
from collections import defaultdict

class Grammar:
    def __init__(self):
        self.productions = {
            # ============ ESTRUCTURA PRINCIPAL ============
            'programa': [
                ['declaracion_global*', 'sentencia*']
            ],
            
            'declaracion_global': [
                ['funcion'],
                ['estructura']
            ],
            
            # ============ DECLARACIONES ============
            'declaracion': [
                ["'chaj'", 'ID', "':'", 'tipo', "'='", 'expresion', "';'"],
                ["'chaj'", 'ID', "'='", 'expresion', "';'"]
            ],
            
            'asignacion': [
                ['ID', "'='", 'expresion', "';'"]
            ],
            
            # ============ FUNCIONES ============
            'funcion': [
                ["'pek''", 'ID', "'('", 'parametros', "')'", "':'", 'tipo', 'bloque'],
                ["'pek''", 'ID', "'('", 'parametros', "')'", 'bloque']
            ],
            
            'parametros': [
                ['parametro', "','", 'parametros'],
                ['parametro'],
                []  # ε (vacío)
            ],
            
            'parametro': [
                ['ID', "':'", 'tipo']
            ],
            
            'llamada_funcion': [
                ["'chok'", 'ID', "'('", 'argumentos', "')'"]
            ],
            
            'argumentos': [
                ['expresion', "','", 'argumentos'],
                ['expresion'],
                []  # ε
            ],
            
            # ============ ESTRUCTURAS DE CONTROL ============
            'condicional': [
                ["'toj'", 'expresion', 'bloque', "'amo ika'", 'bloque'],
                ["'toj'", 'expresion', 'bloque']
            ],
            
            'bucle': [
                ["'muk'", "'('", 'inicio_bucle', "';'", 'condicion', "';'", 'paso', "')'", 'bloque'],  # For-style
                ["'muk'", 'expresion', 'bloque']  # While-style
            ],
            
            'inicio_bucle': [
                ['declaracion'],
                ['asignacion']
            ],
            
            'paso': [
                ['asignacion'],
                ['llamada_funcion']
            ],
            
            # ============ EXPRESIONES ============
            'expresion': [
                ['expresion_logica']
            ],
            
            'expresion_logica': [
                ['expresion_comp', "'īhuān'", 'expresion_logica'],
                ['expresion_comp', "'nozo'", 'expresion_logica'],
                ['expresion_comp']
            ],
            
            'expresion_comp': [
                ['expresion_arit', "'naq'", 'expresion_arit'],
                ['expresion_arit', "'amochīhuanī'", 'expresion_arit'],
                ['expresion_arit', "'tepōztli ichan'", 'expresion_arit'],
                ['expresion_arit', "'tepōztli īhuān'", 'expresion_arit'],
                ['expresion_arit']
            ],
            
            'expresion_arit': [
                ['termino', "'tlen mochīhua'", 'expresion_arit'],  # +
                ['termino', "'tlāzotl'", 'expresion_arit'],       # -
                ['termino']
            ],
            
            'termino': [
                ['factor', "'chīchīltik yāotl'", 'termino'],  # *
                ['factor', "'nextepōllotl'", 'termino'],      # /
                ['factor', "'centēchīuh'", 'termino'],        # %
                ['factor']
            ],
            
            'factor': [
                ["'tlāzotl'", 'factor'],  # -
                ["'no'", 'factor'],       # !
                ['elemento']
            ],
            
            'elemento': [
                ['ID'],
                ['literal'],
                ["'('", 'expresion', "')'"],
                ['llamada_funcion'],
                ['acceso_arreglo'],
                ['acceso_diccionario']
            ],
            
            # ============ TIPOS Y LITERALES ============
            'tipo': [
                ["'loq'"],
                ["'matlaktli'"],
                ["'ompa'"],
                ["'tlāzi'"],
                ["'tlāltikpak'"],
                ["'cuixcoatli'"],
                ['ID']  # Tipos personalizados
            ],
            
            'literal': [
                ['NUMERO'],
                ['CADENA'],
                ["'ja'"],  # true
                ["'ma'"],  # false
                ["'ahmo'"],  # None
                ['lista'],
                ['tupla'],
                ['diccionario']
            ],
            
            'lista': [
                ["'['", 'elementos_lista', "']'"]
            ],
            
            'elementos_lista': [
                ['expresion', "','", 'elementos_lista'],
                ['expresion'],
                []  # ε
            ],
            
            'tupla': [
                ["'('", 'expresion', "','", 'expresion', "'+'", "')'"]
            ],
            
            'diccionario': [
                ["'{'", 'pares_diccionario', "'}'"]
            ],
            
            'pares_diccionario': [
                ['expresion', "':'", 'expresion', "','", 'pares_diccionario'],
                ['expresion', "':'", 'expresion'],
                []  # ε
            ],
            
            # ============ BLOQUES Y ACCESOS ============
            'bloque': [
                ["'b''ah'", 'sentencia*', "'nik''"]
            ],
            
            'sentencia': [
                ['declaracion'],
                ['asignacion'],
                ['condicional'],
                ['bucle'],
                ['imprimir'],
                ['retorno'],
                ['llamada_funcion', "';'"]
            ],
            
            'imprimir': [
                ["'qex'", 'expresion', "','", 'imprimir'],
                ["'qex'", 'expresion', "';'"]
            ],
            
            'retorno': [
                ["'utz''", 'expresion', "';'"],
                ["'utz''", "';'"]
            ],
            
            'acceso_arreglo': [
                ['ID', "'['", 'expresion', "']'"]
            ],
            
            'acceso_diccionario': [
                ['ID', "'['", 'expresion', "':'", 'expresion', "']'"]
            ]
        }

        # Tabla de precedencia de operadores
        self.precedence = [
            ('right', '='),  # Asignación
            ('left', 'nozo'),  # OR
            ('left', 'īhuān'),  # AND
            ('left', 'naq', 'amochīhuanī'),  # ==, !=
            ('nonassoc', 'tepōztli ichan', 'tepōztli īhuān'),  # <, >
            ('left', 'tlen mochīhua', 'tlāzotl'),  # +, -
            ('left', 'chīchīltik yāotl', 'nextepōllotl', 'centēchīuh'),  # *, /, %
            ('right', 'no', 'tlāzotl')  # !, -
        ]

    def get_productions_for(self, symbol):
        """Devuelve todas las producciones para un símbolo no terminal"""
        return self.productions.get(symbol, [])

    def is_terminal(self, symbol):
        """Verifica si un símbolo es terminal"""
        return (symbol.startswith("'") and symbol.endswith("'")) or symbol in [
            'ID', 'NUMERO', 'CADENA'
        ]

    def get_precedence(self, operator):
        """Obtiene la precedencia de un operador"""
        for i, level in enumerate(self.precedence):
            if operator in level[1:]:
                return (i, level[0])  # (nivel, asociatividad)
        return (-1, None)

    def get_expected_tokens(self, current_symbol):
        """Devuelve los tokens esperados para un símbolo dado"""
        expected = set()
        for production in self.get_productions_for(current_symbol):
            first_item = production[0]
            if self.is_terminal(first_item):
                # Eliminar comillas para tokens literales
                expected.add(first_item[1:-1])
            else:
                # Para no terminales, obtener sus primeros tokens
                expected.update(self.get_expected_tokens(first_item))
        return expected

    def validate_structure(self, tokens):
        """Valida básicamente la estructura del código"""
        errors = []
        stack = ['programa']
        pos = 0

        while stack and pos < len(tokens):
            current = stack.pop()
            token = tokens[pos]

            if self.is_terminal(current):
                # Eliminar comillas para comparación
                expected_token = current[1:-1]
                if token['token'] == expected_token:
                    pos += 1
                else:
                    errors.append({
                        'tipo': 'Sintáctico',
                        'mensaje': f"Se esperaba '{expected_token}', se encontró '{token['token']}'",
                        'linea': token['linea'],
                        'posicion': token['posicion']
                    })
            else:
                # Expandir no terminal
                productions = self.get_productions_for(current)
                found = False
                
                for prod in productions:
                    if prod and self._match_production(prod[0], tokens, pos):
                        stack.extend(reversed(prod))  # Añadir en orden inverso
                        found = True
                        break
                
                if not found and productions:
                    expected = self.get_expected_tokens(current)
                    errors.append({
                        'tipo': 'Sintáctico',
                        'mensaje': f"En {current}, se esperaba: {', '.join(expected)}",
                        'linea': tokens[pos]['linea'],
                        'posicion': tokens[pos]['posicion']
                    })

        return errors

    def _match_production(self, symbol, tokens, pos):
        """Verifica si una producción coincide con los tokens actuales"""
        if pos >= len(tokens):
            return False
            
        if self.is_terminal(symbol):
            return tokens[pos]['token'] == symbol[1:-1]
        else:
            # Para no terminales, verificar sus primeras producciones
            for prod in self.get_productions_for(symbol):
                if prod and self._match_production(prod[0], tokens, pos):
                    return True
            return False
        
    def get_used_productions(self, tokens):
        """Devuelve las producciones usadas en el análisis"""
        used = set()
        # Lógica para rastrear producciones usadas
        return list(used)
    
    def calculate_complexity(self):
        """Calcula métricas de complejidad gramatical"""
        return {
            "producciones": len(self.productions),
            "niveles_precedencia": len(self.precedence)
        }
    
    def get_current_state(self):
        """Para reportar estado en errores"""
        return {
            "ultimo_simbolo": self.current_symbol,
            "pila_esperados": self.expected_stack
        }

# Ejemplo de uso
if __name__ == "__main__":
    grammar = Grammar()
    print("Producciones para 'expresion':")
    for prod in grammar.get_productions_for('expresion'):
        print(" → ".join(prod))