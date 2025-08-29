#!/usr/bin/env python3
"""
Intelligent Network Tool

Provides intelligent setup for Retrofit HTTP clients with authentication,
rate limiting, and monitoring features for third-party APIs.
"""

from typing import Any, Dict

from tools.intelligent_base import IntelligentToolBase, IntelligentToolContext


class IntelligentNetworkTool(IntelligentToolBase):
    """Configure Retrofit clients with auth, rate limiting, and monitoring."""

    async def _execute_core_functionality(
        self, context: IntelligentToolContext, arguments: Dict[str, Any]
    ) -> Any:
        api_name = arguments.get("api_name", "ApiService")
        package_name = arguments.get("package_name", "com.example.network")
        base_url = arguments.get("base_url", "https://api.example.com/")
        auth_type = arguments.get("authentication", "none")  # none/bearer/api_key
        rate_limit = int(arguments.get("rate_limit_per_second", 5))
        api_key_name = arguments.get("api_key_name", "X-API-KEY")

        network_dir = self.project_path / "network"
        network_dir.mkdir(parents=True, exist_ok=True)

        service_file = network_dir / f"{api_name}.kt"
        module_file = network_dir / "NetworkModule.kt"

        service_file.write_text(
            self._generate_service_interface(api_name, package_name),
            encoding="utf-8",
        )
        module_file.write_text(
            self._generate_network_module(
                api_name, package_name, base_url, auth_type, api_key_name, rate_limit
            ),
            encoding="utf-8",
        )

        return {
            "service_created": str(service_file),
            "module_created": str(module_file),
            "authentication": auth_type,
            "rate_limit_per_second": rate_limit,
            "monitoring_enabled": True,
        }

    def _generate_service_interface(self, api_name: str, package_name: str) -> str:
        return f"""package {package_name}

import retrofit2.http.GET

interface {api_name} {{
    // TODO: Define API endpoints
    @GET(\"status\")
    suspend fun getStatus(): String
}}
"""

    def _generate_network_module(
        self,
        api_name: str,
        package_name: str,
        base_url: str,
        auth_type: str,
        api_key_name: str,
        rate_limit: int,
    ) -> str:
        auth_header = "Authorization" if auth_type == "bearer" else api_key_name
        auth_value = '\"Bearer $token\"' if auth_type == "bearer" else "token"

        return f"""package {package_name}

import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import okhttp3.Interceptor
import okhttp3.OkHttpClient
import okhttp3.Response
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.moshi.MoshiConverterFactory
import javax.inject.Singleton
import java.util.ArrayDeque

class AuthInterceptor(private val tokenProvider: () -> String?) : Interceptor {{
    override fun intercept(chain: Interceptor.Chain): Response {{
        val token = tokenProvider()
        val request = chain.request().newBuilder().apply {{
            token?.let {{ header("{auth_header}", {auth_value}) }}
        }}.build()
        return chain.proceed(request)
    }}
}}

class RateLimitInterceptor(private val maxRequestsPerSecond: Int) : Interceptor {{
    private val calls = ArrayDeque<Long>()

    @Synchronized
    override fun intercept(chain: Interceptor.Chain): Response {{
        val now = System.currentTimeMillis()
        while (calls.isNotEmpty() && now - calls.peekFirst() > 1000) {{
            calls.removeFirst()
        }}
        if (calls.size >= maxRequestsPerSecond) {{
            val wait = 1000 - (now - calls.peekFirst())
            Thread.sleep(wait)
        }}
        calls.addLast(System.currentTimeMillis())
        return chain.proceed(chain.request())
    }}
}}

class MonitoringInterceptor : Interceptor {{
    override fun intercept(chain: Interceptor.Chain): Response {{
        val start = System.nanoTime()
        val request = chain.request()
        val response = chain.proceed(request)
        val timeMs = (System.nanoTime() - start) / 1e6
        println("HTTP ${request.method} ${request.url} -> ${response.code} in ${timeMs}ms")
        return response
    }}
}}

@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {{
    @Provides
    @Singleton
    fun provideOkHttpClient(): OkHttpClient {{
        val logging = HttpLoggingInterceptor().apply {{ level = HttpLoggingInterceptor.Level.BASIC }}
        return OkHttpClient.Builder()
            .addInterceptor(AuthInterceptor {{ /* TODO: provide token */ null }})
            .addInterceptor(RateLimitInterceptor({rate_limit}))
            .addInterceptor(MonitoringInterceptor())
            .addInterceptor(logging)
            .build()
    }}

    @Provides
    @Singleton
    fun provideRetrofit(client: OkHttpClient): Retrofit =
        Retrofit.Builder()
            .baseUrl("{base_url}")
            .client(client)
            .addConverterFactory(MoshiConverterFactory.create())
            .build()

    @Provides
    @Singleton
    fun provide{api_name}(retrofit: Retrofit): {api_name} =
        retrofit.create({api_name}::class.java)
}}
"""
