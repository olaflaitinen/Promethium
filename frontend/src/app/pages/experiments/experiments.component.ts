import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { Icons } from '../../shared/icons';

interface Experiment {
    id: number;
    name: string;
    description: string;
    job_count: number;
    created_at: string;
    status: 'running' | 'completed' | 'paused';
    metrics?: {
        avg_snr?: number;
        avg_psnr?: number;
        best_run?: string;
    };
}

@Component({
    selector: 'app-experiments',
    standalone: true,
    imports: [CommonModule, RouterLink],
    templateUrl: './experiments.component.html',
    styleUrls: ['./experiments.component.css']
})
export class ExperimentsComponent implements OnInit {
    icons = Icons;
    experiments: Experiment[] = [];
    loading = true;

    private demoExperiments: Experiment[] = [
        {
            id: 1,
            name: 'Denoising Comparison Study',
            description: 'Comparing UNet, Autoencoder, and traditional Wiener filtering on Gulf of Mexico dataset',
            job_count: 12,
            created_at: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
            status: 'completed',
            metrics: { avg_snr: 26.4, avg_psnr: 33.8, best_run: 'UNet V4' }
        },
        {
            id: 2,
            name: 'Interpolation Methods Benchmark',
            description: 'Evaluating missing trace reconstruction algorithms with varying corruption rates',
            job_count: 8,
            created_at: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
            status: 'running',
            metrics: { avg_snr: 22.1, avg_psnr: 29.5 }
        },
        {
            id: 3,
            name: 'Hyperparameter Tuning - GAN',
            description: 'Grid search for optimal GAN parameters on synthetic seismic data',
            job_count: 24,
            created_at: new Date(Date.now() - 14 * 24 * 60 * 60 * 1000).toISOString(),
            status: 'completed',
            metrics: { avg_snr: 24.8, avg_psnr: 31.2, best_run: 'lr=0.0002, batch=64' }
        },
        {
            id: 4,
            name: 'Production Model Validation',
            description: 'Final validation of production models on held-out test set',
            job_count: 4,
            created_at: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
            status: 'paused'
        }
    ];

    ngOnInit() {
        this.loadExperiments();
    }

    loadExperiments() {
        this.loading = true;
        setTimeout(() => {
            this.experiments = this.demoExperiments;
            this.loading = false;
        }, 500);
    }

    getStatusClass(status: string): string {
        switch (status) {
            case 'running': return 'status-running';
            case 'completed': return 'status-completed';
            case 'paused': return 'status-paused';
            default: return '';
        }
    }

    formatDate(date: string): string {
        return new Date(date).toLocaleDateString();
    }
}
