import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService, SystemHealth, SystemMetrics } from '../../services/api.service';
import { Icons } from '../../shared/icons';

@Component({
    selector: 'app-system',
    standalone: true,
    imports: [CommonModule],
    templateUrl: './system.component.html',
    styleUrls: ['./system.component.css']
})
export class SystemComponent implements OnInit {
    icons = Icons;
    health: SystemHealth | null = null;
    metrics: SystemMetrics | null = null;
    loading = true;
    error: string | null = null;

    constructor(private api: ApiService) { }

    ngOnInit() {
        this.loadSystemData();
    }

    loadSystemData() {
        this.loading = true;
        this.error = null;

        this.api.getHealth().subscribe({
            next: (health) => {
                this.health = health;
            },
            error: () => {
                this.health = { status: 'error', version: 'unknown' };
            }
        });

        this.api.getSystemMetrics().subscribe({
            next: (metrics) => {
                this.metrics = metrics;
                this.loading = false;
            },
            error: (err) => {
                this.error = 'Failed to load system metrics';
                this.loading = false;
            }
        });
    }

    getHealthClass(): string {
        if (!this.health) return '';
        switch (this.health.status) {
            case 'ok': return 'health-ok';
            case 'degraded': return 'health-degraded';
            default: return 'health-error';
        }
    }

    getHealthLabel(): string {
        if (!this.health) return 'Unknown';
        switch (this.health.status) {
            case 'ok': return 'All Systems Operational';
            case 'degraded': return 'Degraded Performance';
            default: return 'System Error';
        }
    }
}
