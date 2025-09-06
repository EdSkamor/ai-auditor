#!/usr/bin/env python3
"""
Konfiguracja Cloudflare dla AI Auditor
Integracja z Cloudflare Workers i Pages
"""

import os
import json
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import requests
import hashlib
import hmac
import base64

class CloudflareConfig:
    """Konfiguracja Cloudflare dla AI Auditor."""
    
    def __init__(self):
        self.api_token = os.getenv("CLOUDFLARE_API_TOKEN")
        self.account_id = os.getenv("CLOUDFLARE_ACCOUNT_ID")
        self.zone_id = os.getenv("CLOUDFLARE_ZONE_ID")
        self.domain = os.getenv("CLOUDFLARE_DOMAIN", "ai-auditor-client.com")
        
        # Security
        self.client_secret = "TwojPIN123!"
        self.encryption_key = os.getenv("ENCRYPTION_KEY", "ai-auditor-encryption-key-2024")
        
        # API endpoints
        self.base_url = "https://api.cloudflare.com/client/v4"
        self.worker_url = f"https://ai-auditor.{self.domain}"
        
    def get_headers(self) -> Dict[str, str]:
        """Pobierz nagłówki dla API Cloudflare."""
        return {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
    
    def create_worker(self) -> Dict[str, Any]:
        """Utwórz Cloudflare Worker dla AI Auditor."""
        worker_script = """
// AI Auditor Cloudflare Worker
addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
  const url = new URL(request.url)
  
  // CORS headers
  const corsHeaders = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With',
    'Access-Control-Max-Age': '86400'
  }
  
  // Handle preflight requests
  if (request.method === 'OPTIONS') {
    return new Response(null, { status: 204, headers: corsHeaders })
  }
  
  // Authentication
  const authHeader = request.headers.get('Authorization')
  if (!authHeader || !authHeader.includes('TwojPIN123!')) {
    return new Response(JSON.stringify({error: 'Unauthorized'}), {
      status: 401,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    })
  }
  
  // Route handling
  if (url.pathname === '/health') {
    return new Response(JSON.stringify({
      status: 'ok',
      timestamp: new Date().toISOString(),
      service: 'AI Auditor Cloudflare Worker'
    }), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    })
  }
  
  if (url.pathname === '/upload') {
    return handleFileUpload(request, corsHeaders)
  }
  
  if (url.pathname === '/audit') {
    return handleAuditRequest(request, corsHeaders)
  }
  
  if (url.pathname === '/results') {
    return handleResultsRequest(request, corsHeaders)
  }
  
  return new Response(JSON.stringify({error: 'Not found'}), {
    status: 404,
    headers: { ...corsHeaders, 'Content-Type': 'application/json' }
  })
}

async function handleFileUpload(request, corsHeaders) {
  try {
    const formData = await request.formData()
    const file = formData.get('file')
    
    if (!file) {
      return new Response(JSON.stringify({error: 'No file provided'}), {
        status: 400,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    }
    
    // Store file in Cloudflare KV
    const fileId = generateFileId()
    await AI_AUDITOR_FILES.put(fileId, await file.arrayBuffer())
    
    return new Response(JSON.stringify({
      success: true,
      fileId: fileId,
      filename: file.name,
      size: file.size,
      timestamp: new Date().toISOString()
    }), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    })
  } catch (error) {
    return new Response(JSON.stringify({error: error.message}), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    })
  }
}

async function handleAuditRequest(request, corsHeaders) {
  try {
    const data = await request.json()
    const { fileId, auditType, parameters } = data
    
    // Validate file exists
    const file = await AI_AUDITOR_FILES.get(fileId)
    if (!file) {
      return new Response(JSON.stringify({error: 'File not found'}), {
        status: 404,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    }
    
    // Create audit job
    const jobId = generateJobId()
    const auditJob = {
      id: jobId,
      fileId: fileId,
      auditType: auditType,
      parameters: parameters,
      status: 'pending',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    }
    
    await AI_AUDITOR_JOBS.put(jobId, JSON.stringify(auditJob))
    
    // Queue for processing (in real implementation, this would trigger the local system)
    await queueAuditJob(auditJob)
    
    return new Response(JSON.stringify({
      success: true,
      jobId: jobId,
      status: 'pending',
      message: 'Audit job queued successfully'
    }), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    })
  } catch (error) {
    return new Response(JSON.stringify({error: error.message}), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    })
  }
}

async function handleResultsRequest(request, corsHeaders) {
  try {
    const url = new URL(request.url)
    const jobId = url.searchParams.get('jobId')
    
    if (!jobId) {
      return new Response(JSON.stringify({error: 'Job ID required'}), {
        status: 400,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    }
    
    const job = await AI_AUDITOR_JOBS.get(jobId)
    if (!job) {
      return new Response(JSON.stringify({error: 'Job not found'}), {
        status: 404,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    }
    
    const jobData = JSON.parse(job)
    
    // Get results if available
    const results = await AI_AUDITOR_RESULTS.get(jobId)
    
    return new Response(JSON.stringify({
      job: jobData,
      results: results ? JSON.parse(results) : null
    }), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    })
  } catch (error) {
    return new Response(JSON.stringify({error: error.message}), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    })
  }
}

function generateFileId() {
  return 'file_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now()
}

function generateJobId() {
  return 'job_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now()
}

async function queueAuditJob(auditJob) {
  // In real implementation, this would send a message to the local system
  // For now, we'll just log it
  console.log('Audit job queued:', auditJob.id)
}
"""
        
        worker_config = {
            "name": "ai-auditor-worker",
            "script": worker_script,
            "compatibility_date": "2024-01-15",
            "compatibility_flags": ["nodejs_compat"],
            "bindings": [
                {
                    "name": "AI_AUDITOR_FILES",
                    "type": "kv_namespace",
                    "namespace_id": "ai_auditor_files"
                },
                {
                    "name": "AI_AUDITOR_JOBS", 
                    "type": "kv_namespace",
                    "namespace_id": "ai_auditor_jobs"
                },
                {
                    "name": "AI_AUDITOR_RESULTS",
                    "type": "kv_namespace", 
                    "namespace_id": "ai_auditor_results"
                }
            ]
        }
        
        return worker_config
    
    def create_kv_namespaces(self) -> Dict[str, Any]:
        """Utwórz KV namespaces dla AI Auditor."""
        namespaces = [
            {
                "title": "AI Auditor Files",
                "id": "ai_auditor_files"
            },
            {
                "title": "AI Auditor Jobs",
                "id": "ai_auditor_jobs"
            },
            {
                "title": "AI Auditor Results", 
                "id": "ai_auditor_results"
            }
        ]
        
        return namespaces
    
    def create_dns_records(self) -> Dict[str, Any]:
        """Utwórz rekordy DNS dla AI Auditor."""
        records = [
            {
                "type": "A",
                "name": f"ai-auditor.{self.domain}",
                "content": "192.0.2.1",  # Placeholder IP
                "ttl": 300,
                "proxied": True
            },
            {
                "type": "CNAME",
                "name": f"api.{self.domain}",
                "content": f"ai-auditor.{self.domain}",
                "ttl": 300,
                "proxied": True
            }
        ]
        
        return records
    
    def create_security_rules(self) -> Dict[str, Any]:
        """Utwórz reguły bezpieczeństwa Cloudflare."""
        rules = [
            {
                "name": "AI Auditor Rate Limiting",
                "expression": f"http.host eq \"ai-auditor.{self.domain}\"",
                "action": "rate_limit",
                "rate_limit": {
                    "threshold": 100,
                    "period": 60,
                    "action": "block"
                }
            },
            {
                "name": "AI Auditor Bot Protection",
                "expression": f"http.host eq \"ai-auditor.{self.domain}\" and cf.bot_management.score lt 30",
                "action": "block"
            },
            {
                "name": "AI Auditor File Upload Protection",
                "expression": f"http.host eq \"ai-auditor.{self.domain}\" and http.request.uri.path contains \"/upload\"",
                "action": "challenge"
            }
        ]
        
        return rules
    
    def generate_client_config(self) -> Dict[str, Any]:
        """Wygeneruj konfigurację dla klienta."""
        config = {
            "cloudflare": {
                "worker_url": self.worker_url,
                "api_url": f"https://api.{self.domain}",
                "authentication": {
                    "type": "bearer_token",
                    "token": self.client_secret
                }
            },
            "local_system": {
                "api_endpoint": "http://localhost:8000",
                "web_interface": "http://localhost:8504",
                "authentication": {
                    "password": self.client_secret
                }
            },
            "features": {
                "file_upload": True,
                "audit_processing": True,
                "real_time_results": True,
                "secure_transmission": True
            },
            "limits": {
                "max_file_size": "100MB",
                "max_files_per_upload": 10,
                "rate_limit": "100 requests/minute"
            }
        }
        
        return config
    
    def save_config(self, config: Dict[str, Any], filename: str = "cloudflare_config.json"):
        """Zapisz konfigurację do pliku."""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Konfiguracja zapisana do {filename}")
    
    def create_deployment_script(self) -> str:
        """Utwórz skrypt wdrożenia Cloudflare."""
        script = f"""#!/bin/bash
# AI Auditor Cloudflare Deployment Script

set -e

echo "🚀 Rozpoczynam wdrożenie AI Auditor na Cloudflare..."

# Sprawdź zmienne środowiskowe
if [ -z "$CLOUDFLARE_API_TOKEN" ]; then
    echo "❌ Błąd: CLOUDFLARE_API_TOKEN nie jest ustawiony"
    exit 1
fi

if [ -z "$CLOUDFLARE_ACCOUNT_ID" ]; then
    echo "❌ Błąd: CLOUDFLARE_ACCOUNT_ID nie jest ustawiony"
    exit 1
fi

if [ -z "$CLOUDFLARE_ZONE_ID" ]; then
    echo "❌ Błąd: CLOUDFLARE_ZONE_ID nie jest ustawiony"
    exit 1
fi

echo "✅ Zmienne środowiskowe sprawdzone"

# Utwórz KV namespaces
echo "📦 Tworzenie KV namespaces..."
python3 cloudflare_config.py create-kv

# Wdróż Worker
echo "👷 Wdrażanie Cloudflare Worker..."
wrangler deploy

# Utwórz rekordy DNS
echo "🌐 Tworzenie rekordów DNS..."
python3 cloudflare_config.py create-dns

# Skonfiguruj reguły bezpieczeństwa
echo "🔒 Konfigurowanie reguł bezpieczeństwa..."
python3 cloudflare_config.py create-security

echo "✅ Wdrożenie zakończone pomyślnie!"
echo "🌐 AI Auditor dostępny pod adresem: https://ai-auditor.{self.domain}"
echo "🔑 Hasło dostępu: {self.client_secret}"
"""
        
        return script

def main():
    """Main function."""
    config = CloudflareConfig()
    
    print("🔧 Generowanie konfiguracji Cloudflare dla AI Auditor...")
    
    # Generuj konfigurację
    worker_config = config.create_worker()
    kv_namespaces = config.create_kv_namespaces()
    dns_records = config.create_dns_records()
    security_rules = config.create_security_rules()
    client_config = config.generate_client_config()
    
    # Zapisz konfiguracje
    config.save_config(worker_config, "cloudflare_worker_config.json")
    config.save_config(kv_namespaces, "cloudflare_kv_config.json")
    config.save_config(dns_records, "cloudflare_dns_config.json")
    config.save_config(security_rules, "cloudflare_security_config.json")
    config.save_config(client_config, "client_config.json")
    
    # Utwórz skrypt wdrożenia
    deployment_script = config.create_deployment_script()
    with open("deploy_cloudflare.sh", "w") as f:
        f.write(deployment_script)
    
    os.chmod("deploy_cloudflare.sh", 0o755)
    
    print("✅ Konfiguracja Cloudflare wygenerowana!")
    print("📁 Pliki konfiguracyjne:")
    print("   - cloudflare_worker_config.json")
    print("   - cloudflare_kv_config.json") 
    print("   - cloudflare_dns_config.json")
    print("   - cloudflare_security_config.json")
    print("   - client_config.json")
    print("   - deploy_cloudflare.sh")
    print()
    print("🚀 Aby wdrożyć na Cloudflare:")
    print("   1. Ustaw zmienne środowiskowe:")
    print("      export CLOUDFLARE_API_TOKEN='your_token'")
    print("      export CLOUDFLARE_ACCOUNT_ID='your_account_id'")
    print("      export CLOUDFLARE_ZONE_ID='your_zone_id'")
    print("   2. Uruchom: ./deploy_cloudflare.sh")
    print()
    print("🔑 Hasło dostępu dla klienta: TwojPIN123!")

if __name__ == "__main__":
    main()
