import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { ApiService, DashboardStats, RecentActivity, SystemHealth } from '../../services/api.service';
import { Icons } from '../../shared/icons';

@Component({
    selector: 'app-dashboard',
    standalone: true,
    imports: [CommonModule, RouterLink],
    templateUrl: './dashboard.component.html',
    styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit {
    icons = Icons;
    stats: DashboardStats | null = null;
    health: SystemHealth | null = null;
    activities: RecentActivity[] = [];
    loading = true;
    error: string | null = null;

    constructor(private api: ApiService) { }

    ngOnInit() {
        this.loadDashboardData();
    }

    loadDashboardData() {
        this.loading = true;
        this.error = null;

        // Load health status
        this.api.getHealth().subscribe({
            next: (health) => this.health = health,
            error: () => this.health = { status: 'error', version: '1.0.0' }
        });

        // Load stats
        this.api.getDashboardStats().subscribe({
            next: (stats) => {
                this.stats = stats;
                this.loading = false;
            },
            error: (err) => {
                this.error = 'Failed to load dashboard statistics';
                this.loading = false;
            }
        });

        // Load recent activity
        this.api.getRecentActivity().subscribe({
            next: (activities) => this.activities = activities,
            error: () => this.activities = []
        });
    }

    getStatusClass(status: string): string {
        switch (status) {
            case 'running': return 'status-running';
            case 'completed': return 'status-completed';
            case 'failed': return 'status-failed';
            default: return 'status-pending';
        }
    }

    getTimeAgo(timestamp: string): string {
        const now = new Date();
        const date = new Date(timestamp);
        const diffMs = now.getTime() - date.getTime();
        const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
        const diffDays = Math.floor(diffHours / 24);

        if (diffDays > 0) {
            return diffDays === 1 ? '1 day ago' : `${diffDays} days ago`;
        } else if (diffHours > 0) {
            return diffHours === 1 ? '1 hour ago' : `${diffHours} hours ago`;
        } else {
            return 'Just now';
        }
    }
}
