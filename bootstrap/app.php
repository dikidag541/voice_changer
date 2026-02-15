<?php

use Illuminate\Foundation\Application;
use Illuminate\Foundation\Configuration\Exceptions;
use Illuminate\Foundation\Configuration\Middleware;

// Suppress PHP deprecation warnings to prevent breaking JSON responses
// Using integer bitmask to avoid deprecation warnings about the E_STRICT constant itself on PHP 8.4+
error_reporting(E_ALL & ~E_DEPRECATED & ~2048); 
ini_set('display_errors', '0');

return Application::configure(basePath: dirname(__DIR__))
    ->withRouting(
        web: __DIR__.'/../routes/web.php',
        api: __DIR__.'/../routes/api.php',
        commands: __DIR__.'/../routes/console.php',
        health: '/up',
    )
    ->withMiddleware(function (Middleware $middleware) {
        //
    })
    ->withExceptions(function (Exceptions $exceptions) {
        //
    })->create();
