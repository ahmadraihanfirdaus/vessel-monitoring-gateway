idf_component_register(SRCS "main.c" "esp32_network_client.c" INCLUDE_DIRS "."
    PRIV_REQUIRES esp_timer freertos esp_wifi esp_event esp_netif esp_http_client mbedtls nvs_flash esp_hw_support)
target_compile_options(${COMPONENT_LIB} PRIVATE "-fstack-usage" "-Os")
# Keep the reviewed 1 MiB app partition. Optimize the new networking dependency
# code without changing assertions, TLS validation, certificate roots or flash.
foreach(network_component esp_http_client esp-tls esp_netif lwip nvs_flash)
    idf_component_get_property(network_library ${network_component} COMPONENT_LIB)
    target_compile_options(${network_library} PRIVATE "-Os")
endforeach()
