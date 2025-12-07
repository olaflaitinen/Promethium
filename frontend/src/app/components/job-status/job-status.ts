import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService, Job } from '../../services/api.service';

@Component({
    selector: 'app-job-status',
    standalone: true,
    imports: [CommonModule],
    template: `
    <div class="status-container">
        <h2>Job Status</h2>
        <table class="job-table">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Algorithm</th>
                    <th>Status</th>
                    <th>Created At</th>
                </tr>
            </thead>
            <tbody>
                <tr *ngFor="let job of jobs()">
                    <td>{{ job.id }}</td>
                    <td>{{ job.algorithm }}</td>
                    <td [class]="job.status.toLowerCase()">{{ job.status }}</td>
                    <td>{{ job.created_at | date:'short' }}</td>
                </tr>
            </tbody>
        </table>
    </div>
  `,
    styles: [`
    .status-container { padding: 20px; }
    .job-table { width: 100%; border-collapse: collapse; }
    th, td { padding: 10px; border-bottom: 1px solid #eee; text-align: left; }
    .completed { color: green; font-weight: bold; }
    .failed { color: red; font-weight: bold; }
    .running { color: orange; font-weight: bold; }
  `]
})
export class JobStatusComponent implements OnInit {
    jobs = signal<Job[]>([]);

    constructor(private api: ApiService) { }

    ngOnInit() {
        this.pollJobs();
    }

    pollJobs() {
        this.api.getJobs().subscribe((data: Job[]) => this.jobs.set(data));
        // Simple polling every 5s
        setInterval(() => {
            this.api.getJobs().subscribe((data: Job[]) => this.jobs.set(data));
        }, 5000);
    }
}
