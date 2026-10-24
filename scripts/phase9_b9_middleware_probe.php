<?php
// Stand-ins ONLY for running the real production middleware in a DB-free CLI.
namespace Symfony\Component\HttpFoundation {
    class Response {
        public function __construct(public int $status = 200, public array $data = []) {}
    }
}
namespace Illuminate\Http {
    class JsonResponse extends \Symfony\Component\HttpFoundation\Response {}
    class Headers {
        public function __construct(private array $fields) {}
        public function get(string $key): ?string { return $this->fields[strtolower($key)] ?? null; }
    }
    class Request {
        public Headers $headers;
        public function __construct(private string $content, private string $type, ?string $length) {
            $this->headers = new Headers(['content-length' => $length, 'content-type' => $type]);
        }
        public function getContent(): string { return $this->content; }
        public function header(string $key, ?string $default = null): ?string {
            return $this->headers->get($key) ?? $default;
        }
    }
}
namespace {
    class FakeResponseFactory {
        public function json(array $data, int $status): \Illuminate\Http\JsonResponse {
            return new \Illuminate\Http\JsonResponse($status, $data);
        }
    }
    function response(): FakeResponseFactory { return new FakeResponseFactory(); }
    require dirname(__DIR__).'/backend/laravel/app/Http/Middleware/EnsureTelemetryPayloadSize.php';
    $cases = json_decode(stream_get_contents(STDIN), true, 512, JSON_THROW_ON_ERROR);
    $middleware = new \App\Http\Middleware\EnsureTelemetryPayloadSize();
    foreach ($cases as $case) {
        $req = new \Illuminate\Http\Request($case['body'], $case['type'], $case['length']);
        $result = $middleware->handle(
            $req,
            static fn ($request) => new \Symfony\Component\HttpFoundation\Response(200, ['passed' => true])
        );
        echo json_encode(['status' => $result->status, 'data' => $result->data], JSON_THROW_ON_ERROR), "\n";
    }
}
