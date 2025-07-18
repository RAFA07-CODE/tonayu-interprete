<?php
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');
header('Content-Type: application/json; charset=utf-8');

ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

$logFile = __DIR__.'/tonayu_errors.log';
file_put_contents($logFile, "\n".date('[Y-m-d H:i:s]')." Nueva ejecución\n", FILE_APPEND);

try {
    // Obtener datos de entrada
    $input = file_get_contents('php://input');
    $data = json_decode($input, true) ?: [];
    $codigo = $data['codigo'] ?? '';
    
    if (empty(trim($codigo))) {
        throw new Exception("El código fuente está vacío");
    }

    // Crear archivo temporal
    $tempDir = __DIR__.'/tmp';
    if (!file_exists($tempDir)) {
        mkdir($tempDir, 0755, true);
    }
    
    $tempFile = $tempDir.'/tonayu_'.time().'_'.bin2hex(random_bytes(4)).'.ton';
    file_put_contents($tempFile, $codigo);

    // Ejecutar intérprete
    $command = 'python '.escapeshellarg(__DIR__.'/interpreter.py').' '.escapeshellarg($tempFile).' 2>&1';
    $output = shell_exec($command);
    
    if ($output === null) {
        throw new Exception("El intérprete no devolvió ninguna salida");
    }

    // Procesar salida
    $result = json_decode($output, true);
    if (json_last_error() !== JSON_ERROR_NONE) {
        throw new Exception("Error en formato JSON: ".json_last_error_msg());
    }

    // Respuesta
    http_response_code(200);
    echo json_encode($result, JSON_UNESCAPED_UNICODE);

} catch (Exception $e) {
    http_response_code(500);
    echo json_encode([
        'error' => 'Error en el servidor',
        'detalle' => $e->getMessage(),
        'soporte' => 'contacto@tonayu.lang'
    ], JSON_UNESCAPED_UNICODE);
    
} finally {
    if (isset($tempFile) && file_exists($tempFile)) {
        @unlink($tempFile);
    }
}
?>