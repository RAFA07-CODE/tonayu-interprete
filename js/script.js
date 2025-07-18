    /* =====================================================
       MANEJO DE NÚMEROS DE LÍNEA Y ENVÍO DE CÓDIGO
       ===================================================== */
    document.addEventListener('DOMContentLoaded', function () {
      // Elementos DOM principales.
      const textarea = document.getElementById('codigo');         // Área de código fuente.
      const lineNumbers = document.querySelector('.line-numbers'); // Columna de números de línea.

      /* -----------------------------------------------------
         Función: updateLineNumbers
         Propósito: sincronizar la cantidad de líneas que se
         muestran en la columna lateral con el texto actual.
      ----------------------------------------------------- */
      function updateLineNumbers() {
        const lineas = textarea.value.split('\n');                  // Divide por saltos de línea.
        lineNumbers.innerHTML = lineas.map((_, i) => (i + 1) + '<br>').join(''); // Genera HTML.
      }

      // Actualiza al cargar y cada vez que el usuario escriba.
      textarea.addEventListener('input', updateLineNumbers);
      updateLineNumbers();

      // ---------- ENVÍO MANUAL ----------
      document.getElementById('form').addEventListener('submit', function (e) {
        e.preventDefault();           // Evita recargar la página.
        ejecutarCodigo(false);        // Llama a la función con modo normal.
      });

      /* =====================================================
         🔄 MOD: AUTO-EJECUCIÓN DINÁMICA
         ===================================================== */

      /* -----------------------------------------------------
         Función: debounce
         Propósito: esperar un tiempo (delay) después del
         último evento antes de ejecutar la función "fn".
         Evita llamadas excesivas al servidor mientras el
         usuario escribe.
      ----------------------------------------------------- */
      const debounce = (fn, delay = 1000) => { // 1000 ms = 1 s.
        let temporizador;                      // Identificador del timeout.
        return (...args) => {                  // Devuelve función wrapper.
          clearTimeout(temporizador);          // Reinicia el conteo.
          temporizador = setTimeout(() => fn(...args), delay); // Ejecuta tras delay.
        };
      };

      /* -----------------------------------------------------
         Función: ejecutarCodigoDebounce
         Propósito: ejecutar el código de forma silenciosa
         cuando el checkbox "Auto-ejecutar" esté marcado.
      ----------------------------------------------------- */
      const ejecutarCodigoDebounce = debounce(() => {
        const autoEjecutar = document.getElementById('auto-ejecutar').checked; // Verifica checkbox.
        if (autoEjecutar) {
          ejecutarCodigo(true); // Llamada en modo silencioso.
        }
      });

      // Cada vez que se escribe algo, disparar debounce.
      textarea.addEventListener('input', ejecutarCodigoDebounce);

      /* =====================================================
         SELECTOR DE IDIOMA
         ===================================================== */
      const languageSelector = document.getElementById('language-selector');

      languageSelector.addEventListener('change', function () {
        const selectedLanguage = this.value;
        updateLanguage(selectedLanguage);
      });

      function updateLanguage(lang) {
        document.querySelectorAll('[data-es], [data-nah]').forEach(element => {
          if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA' || element.tagName === 'SELECT') {
            // No cambiar elementos de entrada
            return;
          }

          const text = element.getAttribute(`data-${lang}`);
          if (text) {
            if (element.hasAttribute('placeholder')) {
              element.setAttribute('placeholder', text);
            } else {
              element.textContent = text;
            }
          }
        });
      }
    });

    /* =====================================================
       Función principal: ejecutarCodigo
       Parámetros:
         silencioso → true  = llamada automática
                      false = llamada manual (botón)
       ----------------------------------------------------- */
    async function ejecutarCodigo(silencioso = false) {
      const btn = document.getElementById('ejecutar-btn'); // Botón Ejecutar.
      const statusElement = document.getElementById('console-status');

      if (!silencioso) {                                   // Sólo en modo manual:
        btn.disabled = true;                               // Deshabilita botón.
        const currentLang = document.getElementById('language-selector').value;
        btn.textContent = currentLang === 'es' ? 'Procesando…' : 'Tictlaliztli…';
        statusElement.textContent = currentLang === 'es' ? 'Ejecutando...' : 'Tictlaliztli...';
        statusElement.className = 'console-status warning';
      }

      try {
        const codigo = document.getElementById('codigo').value; // Obtiene código.

        // Envía petición a PHP.
        const response = await fetch('ejecutar.php', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ codigo })
        });

        // Manejo de respuesta HTTP.
        if (!response.ok) {
          const error = await response.json().catch(() => null);
          throw new Error(error?.detalle || `Error ${response.status}`);
        }

        // Parseo de JSON resultante.
        const data = await response.json();
        if (data.error) throw new Error(data.error);

        mostrarResultados(data);  // Renderiza todo.
        const currentLang = document.getElementById('language-selector').value;
        statusElement.textContent = currentLang === 'es' ? 'Éxito' : 'Tlami';
        statusElement.className = 'console-status success';

        if (!silencioso) document.getElementById('reportes').scrollIntoView({ behavior: 'smooth' });

      } catch (error) {
        console.error('Error completo:', error);
        const currentLang = document.getElementById('language-selector').value;
        statusElement.textContent = currentLang === 'es' ? 'Error' : 'Ahmo tlami';
        statusElement.className = 'console-status error';

        document.getElementById('resultado').innerHTML = `
          <div class="error-message">
            <div class="error-icon">❌</div>
            <div>
              <h3>${currentLang === 'es' ? 'Error en la ejecución' : 'Ahcoltiliztli ipan tictlaliztli'}</h3>
              <p>${escapeHtml(error.message)}</p>
              <small class="error-detail">${currentLang === 'es' ? 'Verifica la consola para detalles técnicos' : 'Xiquitta consola iccampa tlamantli'}</small>
            </div>
          </div>`;
      } finally {
        if (!silencioso) {        // Sólo reactiva botón si era llamada manual.
          btn.disabled = false;
          const currentLang = document.getElementById('language-selector').value;
          btn.textContent = currentLang === 'es' ? '▶ Ejecutar' : '▶ Tictlaliz';
        }
      }
    }

    /* =====================================================
       Función: mostrarResultados
       Propósito: pintar la salida del programa y
                  los errores (léxicos, sintácticos, semánticos)
       ===================================================== */

    function mostrarResultados(data) {
      const divResultado = document.getElementById('resultado');
      let htmlSalida = '';
      const currentLang = document.getElementById('language-selector').value;

      if (data.error) {
        htmlSalida = `
      <div class="error-message">
        <div class="error-icon">❌</div>
        <div>
          <h3>${currentLang === 'es' ? 'Error en la ejecución' : 'Ahcoltiliztli ipan tictlaliztli'}</h3>
          <p>${escapeHtml(data.error)}</p>
        </div>
      </div>`;
      } else {
        const textoConsola = 'console_output' in data
          ? (data.console_output || `<span class="no-output">${currentLang === 'es' ? '(sin salida)' : '(ahmo tlalpanaliztli)'}</span>`)
          : `<span class="no-output">${currentLang === 'es' ? '(sin salida)' : '(ahmo tlalpanaliztli)'}</span>`;

        htmlSalida += `
      <div class="console-output-section">
        <h3>💻 ${currentLang === 'es' ? 'Salida del programa' : 'Tlalpanaliztli tlen programa'}</h3>
        <div class="output-content">${textoConsola.replace(/\n/g, '<br>')}</div>
      </div>`;

        // ✅ Agregado: Derivación del árbol sintáctico
        if (data.derivacion) {
          htmlSalida += `
        <div class="derivacion-section">
          <h3>📘 ${currentLang === 'es' ? 'Derivación del programa' : 'Tlahtolpehpenalistli tlen tlahtolli'}</h3>
          <pre class="derivacion-block">${escapeHtml(data.derivacion)}</pre>
        </div>`;
        }

        /* ---------- Mostrar errores (si los hay) ---------- */
        const erroresLexicos = data.analisis?.lexico?.errores || [];
        const erroresSintacticos = data.analisis?.sintactico?.errores || [];
        const erroresSemanticos = data.analisis?.semantico?.errores || [];

        const totalErrores = erroresLexicos.length + erroresSintacticos.length + erroresSemanticos.length;

        if (totalErrores > 0) {
          htmlSalida += `
    <div class="error-section">
      <h3>❌ ${currentLang === 'es'
              ? `Errores de análisis (${totalErrores})`
              : `Ahcoltiliztli ipan tlamachiliztli (${totalErrores})`}</h3>
      <div class="error-list">
        ${erroresLexicos.map(e => `
          <div class="error-line">
            <span class="error-icon">🟥</span>
            <span>
              <strong>${currentLang === 'es' ? `Línea ${e.linea}:` : `Tlapalli ${e.linea}:`}</strong>
              [${currentLang === 'es' ? 'Léxico' : 'Tlahtoltlamachiliztli'}] ${escapeHtml(e.mensaje)}
            </span>
          </div>`).join('')}

        ${erroresSintacticos.map(e => `
          <div class="error-line">
            <span class="error-icon">🟧</span>
            <span>
              <strong>${currentLang === 'es' ? `Línea ${e.linea}:` : `Tlapalli ${e.linea}:`}</strong>
              [${currentLang === 'es' ? 'Sintáctico' : 'Tlahtolpehpenalistli'}] ${escapeHtml(e.mensaje)}
            </span>
          </div>`).join('')}

        ${erroresSemanticos.map(e => `
          <div class="error-line">
            <span class="error-icon">🟨</span>
            <span>
              <strong>${currentLang === 'es' ? `Línea ${e.linea}:` : `Tlapalli ${e.linea}:`}</strong>
              [${currentLang === 'es' ? 'Semántico' : 'Tlamachiliztli'}] ${escapeHtml(e.mensaje)}
            </span>
          </div>`).join('')}
      </div>
    </div>`;
        } else {
          htmlSalida += `
    <div class="execution-status">
      <span class="success-icon">✓</span>
      <span>${currentLang === 'es'
              ? 'Ejecución completada sin errores'
              : 'Tictlaliztli tlami ahmo ahcoltiliztli'}</span>
    </div>`;
        }

      }

      divResultado.innerHTML = htmlSalida;

      const divLexico = document.getElementById('lexico');
      if (data.analisis?.lexico) {
        const lex = data.analisis.lexico;
        divLexico.innerHTML = `
      <div class="analysis-section">
        <h2 class="section-title">🔍 ${currentLang === 'es' ? 'Análisis Léxico' : 'Tlahtoltlamachiliztli'}</h2>
        <div class="analysis-summary">
          <p><strong>${currentLang === 'es' ? 'Total tokens:' : 'Tlapohualiztli tokens:'}</strong> ${lex.total_tokens}</p>
          ${lex.errores.length
            ? `<p class="error-count"><strong>${currentLang === 'es' ? 'Errores:' : 'Ahcoltiliztli:'}</strong> ${lex.errores.length}</p>`
            : `<p class="success-message">✓ ${currentLang === 'es' ? 'Análisis correcto' : 'Tlamachiliztli tlami'}</p>`}
        </div>
        ${generarTablaTokens(lex.tokens)}
        ${lex.errores.length ? generarListaErrores(lex.errores) : ''}
      </div>`;
      }

      function escapeHtml(str) {
        return str.replace(/[&<>"']/g, c => ({
          '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;'
        }[c]));
      }

      function generarTablaTokens(tokens) {
        return `
    <div class="table-container">
      <table class="token-table">
        <thead>
          <tr>
            <th>#</th>
            <th>Token</th>
            <th>${currentLang === 'es' ? 'Tipo' : 'Tlamantli'}</th>
            <th>${currentLang === 'es' ? 'Línea' : 'Tlapalli'}</th>
            <th>${currentLang === 'es' ? 'Significado Náhuatl' : 'Tlahtolli náhuatl'}</th>
          </tr>
        </thead>
        <tbody>
          ${tokens.map((t, i) => `
            <tr>
              <td>${i + 1}</td>
              <td><code>${escapeHtml(t.token)}</code></td>
              <td><span class="token-tag ${t.tipo ? t.tipo.toLowerCase() : ''}">${t.tipo || '—'}</span></td>              
              <td>${t.linea || '—'}</td>
              <td class="nahuatl">${t.nahuatl || '—'}</td>
            </tr>`).join('')}
        </tbody>
      </table>
    </div>`;
      }

      function generarListaErrores(errs) {
        return `
      <div class="error-details">
        <h3>${currentLang === 'es' ? 'Detalles de errores léxicos:' : 'Tlamantli ahcoltiliztli tlahtoltlamachiliztli:'}</h3>
        <ul class="error-list">
          ${errs.map(e => `
            <li>
              <strong>${currentLang === 'es' ? `Línea ${e.linea}:` : `Tlapalli ${e.linea}:`}</strong> ${escapeHtml(e.mensaje)}
            </li>`).join('')}
        </ul>
      </div>`;
      }
    }
