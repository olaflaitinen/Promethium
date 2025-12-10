import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { Icons } from '../../shared/icons';

interface Benchmark {
    id: number;
    name: string;
    description: string;
    status: 'pending' | 'running' | 'completed' | 'failed';
    config: object;
    started_at?: string;
    completed_at?: string;
    duration_seconds?: number;
    metrics?: {
        snr?: number;
        psnr?: number;
        ssim?: number;
        processing_time?: number;
    };
}

@Component({
    selector: 'app-benchmarks',
    standalone: true,
    imports: [CommonModule, RouterLink],
    templateUrl: './benchmarks.component.html',
    styleUrls: ['./benchmarks.component.css']
})
export class BenchmarksComponent implements OnInit {
    icons = Icons;
    benchmarks: Benchmark[] = [];
    loading = true;

    private demoBenchmarks: Benchmark[] = [
        {
            id: 1,
            name: 'Standard Denoising Benchmark',
            description: 'Evaluate denoising performance on standard test datasets',
            status: 'completed',
            config: { dataset: 'gulf_mexico_test', models: ['unet-v4', 'ae-v2'] },
            started_at: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
            completed_at: new Date(Date.now() - 1.5 * 24 * 60 * 60 * 1000).toISOString(),
            duration_seconds: 43200,
            metrics: { snr: 28.5, psnr: 35.2, ssim: 0.94, processing_time: 12.5 }
        },
        {
            id: 2,
            name: 'Interpolation Quality Assessment',
            description: 'Missing trace reconstruction with varying corruption rates (10%, 30%, 50%)',
            status: 'running',
            config: { dataset: 'synthetic_marmousi', corruption_rates: [0.1, 0.3, 0.5] },
            started_at: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
            metrics: { snr: 22.1, psnr: 29.5 }
        },
        {
            id: 3,
            name: 'High-Noise Resilience Test',
            description: 'Evaluate model performance under extreme noise conditions',
            status: 'pending',
            config: { noise_levels: [-5, 0, 5, 10], models: ['unet-v4'] }
        },
        {
            id: 4,
            name: 'Production Latency Benchmark',
            description: 'Measure inference latency for production deployment requirements',
            status: 'completed',
            config: { batch_sizes: [1, 8, 32], hardware: 'gpu' },
            started_at: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
            completed_at: new Date(Date.now() - 4.8 * 24 * 60 * 60 * 1000).toISOString(),
            duration_seconds: 17280,
            metrics: { processing_time: 0.45, snr: 27.8 }
        }
    ];

    ngOnInit() {
        this.loadBenchmarks();
    }

    loadBenchmarks() {
        this.loading = true;
        setTimeout(() => {
            this.benchmarks = this.demoBenchmarks;
            this.loading = false;
        }, 500);
    }

    runBenchmark(benchmark: Benchmark) {
        benchmark.status = 'running';
        benchmark.started_at = new Date().toISOString();
    }

    getStatusClass(status: string): string {
        switch (status) {
            case 'running': return 'status-running';
            case 'completed': return 'status-completed';
            case 'failed': return 'status-failed';
            default: return 'status-pending';
        }
    }

    formatDuration(seconds?: number): string {
        if (!seconds) return '-';
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        if (hours > 0) return `${hours}h ${minutes}m`;
        return `${minutes}m`;
    }

    formatDate(date?: string): string {
        if (!date) return '-';
        return new Date(date).toLocaleString();
    }
}
