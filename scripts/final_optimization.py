#!/usr/bin/env python3
"""
Optymalizacje końcowe i testy systemu AI Auditor.
"""

import sys
import os
import logging
import time
import psutil
import gc
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SystemOptimizer:
    """Optymalizator systemu."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.optimization_results = {}
    
    def check_system_resources(self) -> Dict[str, Any]:
        """Sprawdzenie zasobów systemowych."""
        self.logger.info("🔍 Sprawdzanie zasobów systemowych...")
        
        # CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        
        # Memory
        memory = psutil.virtual_memory()
        memory_gb = memory.total / (1024**3)
        memory_used_gb = memory.used / (1024**3)
        memory_percent = memory.percent
        
        # Disk
        disk = psutil.disk_usage('/')
        disk_gb = disk.total / (1024**3)
        disk_used_gb = disk.used / (1024**3)
        disk_percent = (disk.used / disk.total) * 100
        
        # GPU (if available)
        gpu_info = {}
        try:
            import torch
            if torch.cuda.is_available():
                gpu_info = {
                    'available': True,
                    'device_name': torch.cuda.get_device_name(0),
                    'memory_total': torch.cuda.get_device_properties(0).total_memory / (1024**3),
                    'memory_allocated': torch.cuda.memory_allocated(0) / (1024**3),
                    'memory_cached': torch.cuda.memory_reserved(0) / (1024**3)
                }
            else:
                gpu_info = {'available': False}
        except ImportError:
            gpu_info = {'available': False, 'error': 'PyTorch not available'}
        
        resources = {
            'cpu': {
                'count': cpu_count,
                'usage_percent': cpu_percent,
                'status': 'good' if cpu_percent < 80 else 'warning' if cpu_percent < 95 else 'critical'
            },
            'memory': {
                'total_gb': round(memory_gb, 2),
                'used_gb': round(memory_used_gb, 2),
                'usage_percent': memory_percent,
                'status': 'good' if memory_percent < 80 else 'warning' if memory_percent < 95 else 'critical'
            },
            'disk': {
                'total_gb': round(disk_gb, 2),
                'used_gb': round(disk_used_gb, 2),
                'usage_percent': round(disk_percent, 2),
                'status': 'good' if disk_percent < 80 else 'warning' if disk_percent < 95 else 'critical'
            },
            'gpu': gpu_info
        }
        
        self.optimization_results['system_resources'] = resources
        return resources
    
    def optimize_memory_usage(self) -> Dict[str, Any]:
        """Optymalizacja użycia pamięci."""
        self.logger.info("🧠 Optymalizacja użycia pamięci...")
        
        # Force garbage collection
        before_gc = psutil.virtual_memory().used / (1024**3)
        gc.collect()
        after_gc = psutil.virtual_memory().used / (1024**3)
        freed_mb = (before_gc - after_gc) * 1024
        
        # Clear Python cache
        import sys
        cache_cleared = 0
        for module_name in list(sys.modules.keys()):
            if hasattr(sys.modules[module_name], '__file__'):
                cache_cleared += 1
        
        optimization = {
            'memory_freed_mb': round(freed_mb, 2),
            'cache_cleared': cache_cleared,
            'timestamp': datetime.now().isoformat()
        }
        
        self.optimization_results['memory_optimization'] = optimization
        return optimization
    
    def optimize_file_system(self) -> Dict[str, Any]:
        """Optymalizacja systemu plików."""
        self.logger.info("📁 Optymalizacja systemu plików...")
        
        # Check for large files
        large_files = []
        temp_dirs = ['/tmp', '/var/tmp']
        
        for temp_dir in temp_dirs:
            if os.path.exists(temp_dir):
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        try:
                            size = os.path.getsize(file_path)
                            if size > 100 * 1024 * 1024:  # 100MB
                                large_files.append({
                                    'path': file_path,
                                    'size_mb': round(size / (1024**2), 2)
                                })
                        except (OSError, IOError):
                            continue
        
        # Check disk space
        disk_usage = psutil.disk_usage('/')
        free_space_gb = disk_usage.free / (1024**3)
        
        optimization = {
            'large_files_found': len(large_files),
            'large_files': large_files[:10],  # Top 10
            'free_space_gb': round(free_space_gb, 2),
            'recommendation': 'cleanup' if free_space_gb < 10 else 'ok'
        }
        
        self.optimization_results['filesystem_optimization'] = optimization
        return optimization
    
    def optimize_network_connections(self) -> Dict[str, Any]:
        """Optymalizacja połączeń sieciowych."""
        self.logger.info("🌐 Optymalizacja połączeń sieciowych...")
        
        # Check open connections
        connections = psutil.net_connections()
        tcp_connections = [c for c in connections if c.type == 1]  # TCP
        udp_connections = [c for c in connections if c.type == 2]  # UDP
        
        # Check listening ports
        listening_ports = [c.laddr.port for c in connections if c.status == 'LISTEN']
        
        optimization = {
            'total_connections': len(connections),
            'tcp_connections': len(tcp_connections),
            'udp_connections': len(udp_connections),
            'listening_ports': listening_ports,
            'recommendation': 'ok' if len(connections) < 1000 else 'review'
        }
        
        self.optimization_results['network_optimization'] = optimization
        return optimization
    
    def optimize_database_performance(self) -> Dict[str, Any]:
        """Optymalizacja wydajności bazy danych."""
        self.logger.info("🗄️ Optymalizacja wydajności bazy danych...")
        
        # Check for database files
        db_files = []
        data_dir = Path.home() / '.ai-auditor'
        
        if data_dir.exists():
            for db_file in data_dir.rglob('*.db'):
                try:
                    size = db_file.stat().st_size
                    db_files.append({
                        'path': str(db_file),
                        'size_mb': round(size / (1024**2), 2)
                    })
                except (OSError, IOError):
                    continue
        
        optimization = {
            'database_files': len(db_files),
            'total_size_mb': sum(db['size_mb'] for db in db_files),
            'files': db_files,
            'recommendation': 'ok' if len(db_files) < 10 else 'review'
        }
        
        self.optimization_results['database_optimization'] = optimization
        return optimization
    
    def run_performance_tests(self) -> Dict[str, Any]:
        """Uruchomienie testów wydajności."""
        self.logger.info("⚡ Uruchamianie testów wydajności...")
        
        tests = {}
        
        # Test 1: CPU Performance
        start_time = time.time()
        for i in range(1000000):
            _ = i * i
        cpu_time = time.time() - start_time
        tests['cpu_performance'] = {
            'time_seconds': round(cpu_time, 3),
            'status': 'good' if cpu_time < 1.0 else 'warning' if cpu_time < 2.0 else 'slow'
        }
        
        # Test 2: Memory Performance
        start_time = time.time()
        data = [i for i in range(100000)]
        memory_time = time.time() - start_time
        del data
        tests['memory_performance'] = {
            'time_seconds': round(memory_time, 3),
            'status': 'good' if memory_time < 0.1 else 'warning' if memory_time < 0.5 else 'slow'
        }
        
        # Test 3: File I/O Performance
        start_time = time.time()
        test_file = Path('/tmp/ai_auditor_test.tmp')
        with open(test_file, 'w') as f:
            f.write('test' * 10000)
        with open(test_file, 'r') as f:
            _ = f.read()
        test_file.unlink()
        io_time = time.time() - start_time
        tests['io_performance'] = {
            'time_seconds': round(io_time, 3),
            'status': 'good' if io_time < 0.1 else 'warning' if io_time < 0.5 else 'slow'
        }
        
        self.optimization_results['performance_tests'] = tests
        return tests
    
    def generate_optimization_report(self) -> Dict[str, Any]:
        """Generowanie raportu optymalizacji."""
        self.logger.info("📊 Generowanie raportu optymalizacji...")
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'system_info': {
                'platform': sys.platform,
                'python_version': sys.version,
                'hostname': os.uname().nodename if hasattr(os, 'uname') else 'unknown'
            },
            'optimization_results': self.optimization_results,
            'recommendations': self._generate_recommendations(),
            'overall_status': self._calculate_overall_status()
        }
        
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """Generowanie rekomendacji optymalizacji."""
        recommendations = []
        
        # Check system resources
        if 'system_resources' in self.optimization_results:
            resources = self.optimization_results['system_resources']
            
            if resources['cpu']['status'] == 'critical':
                recommendations.append("⚠️ CPU usage is critical - consider reducing workload")
            elif resources['cpu']['status'] == 'warning':
                recommendations.append("⚠️ CPU usage is high - monitor system performance")
            
            if resources['memory']['status'] == 'critical':
                recommendations.append("⚠️ Memory usage is critical - consider adding RAM")
            elif resources['memory']['status'] == 'warning':
                recommendations.append("⚠️ Memory usage is high - monitor memory usage")
            
            if resources['disk']['status'] == 'critical':
                recommendations.append("⚠️ Disk space is critical - free up space immediately")
            elif resources['disk']['status'] == 'warning':
                recommendations.append("⚠️ Disk space is low - consider cleanup")
        
        # Check filesystem
        if 'filesystem_optimization' in self.optimization_results:
            fs_opt = self.optimization_results['filesystem_optimization']
            if fs_opt['recommendation'] == 'cleanup':
                recommendations.append("🧹 Consider cleaning up large temporary files")
        
        # Check network
        if 'network_optimization' in self.optimization_results:
            net_opt = self.optimization_results['network_optimization']
            if net_opt['recommendation'] == 'review':
                recommendations.append("🌐 Review network connections - high number detected")
        
        # Check performance tests
        if 'performance_tests' in self.optimization_results:
            perf_tests = self.optimization_results['performance_tests']
            for test_name, test_result in perf_tests.items():
                if test_result['status'] == 'slow':
                    recommendations.append(f"⚡ {test_name} is slow - consider hardware upgrade")
        
        if not recommendations:
            recommendations.append("✅ System is running optimally")
        
        return recommendations
    
    def _calculate_overall_status(self) -> str:
        """Obliczenie ogólnego statusu systemu."""
        critical_count = 0
        warning_count = 0
        
        # Check system resources
        if 'system_resources' in self.optimization_results:
            resources = self.optimization_results['system_resources']
            for resource_type in ['cpu', 'memory', 'disk']:
                if resources[resource_type]['status'] == 'critical':
                    critical_count += 1
                elif resources[resource_type]['status'] == 'warning':
                    warning_count += 1
        
        # Check performance tests
        if 'performance_tests' in self.optimization_results:
            perf_tests = self.optimization_results['performance_tests']
            for test_result in perf_tests.values():
                if test_result['status'] == 'slow':
                    warning_count += 1
        
        if critical_count > 0:
            return 'critical'
        elif warning_count > 2:
            return 'warning'
        else:
            return 'good'
    
    def save_report(self, report: Dict[str, Any], output_path: Path = None):
        """Zapisanie raportu optymalizacji."""
        if output_path is None:
            output_path = Path.home() / '.ai-auditor' / 'optimization_report.json'
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"📄 Raport optymalizacji zapisany: {output_path}")


def main():
    """Main optimization function."""
    print("🚀 AI Auditor - Optymalizacje końcowe")
    print("=====================================")
    
    optimizer = SystemOptimizer()
    
    try:
        # Run all optimizations
        print("\n🔍 Sprawdzanie zasobów systemowych...")
        optimizer.check_system_resources()
        
        print("\n🧠 Optymalizacja pamięci...")
        optimizer.optimize_memory_usage()
        
        print("\n📁 Optymalizacja systemu plików...")
        optimizer.optimize_file_system()
        
        print("\n🌐 Optymalizacja połączeń sieciowych...")
        optimizer.optimize_network_connections()
        
        print("\n🗄️ Optymalizacja bazy danych...")
        optimizer.optimize_database_performance()
        
        print("\n⚡ Testy wydajności...")
        optimizer.run_performance_tests()
        
        # Generate and save report
        print("\n📊 Generowanie raportu...")
        report = optimizer.generate_optimization_report()
        optimizer.save_report(report)
        
        # Display summary
        print("\n📋 PODSUMOWANIE OPTYMALIZACJI")
        print("=" * 40)
        
        print(f"Status ogólny: {report['overall_status'].upper()}")
        print(f"Timestamp: {report['timestamp']}")
        
        print("\n🔧 REKOMENDACJE:")
        for i, rec in enumerate(report['recommendations'], 1):
            print(f"{i}. {rec}")
        
        print(f"\n📄 Pełny raport zapisany w: {Path.home() / '.ai-auditor' / 'optimization_report.json'}")
        
        return 0 if report['overall_status'] == 'good' else 1
        
    except Exception as e:
        print(f"\n❌ Błąd podczas optymalizacji: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
