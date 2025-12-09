import { Component, OnInit } from '@angular/core';
import { CommonModule, DatePipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService, Dataset, Job, JobCreate, JobStatus, Model } from '../../services/api.service';
import { Icons } from '../../shared/icons';

@Component({
    selector: 'app-job-submission',
    standalone: true,
    imports: [CommonModule, FormsModule, DatePipe],
    templateUrl: './job-submission.component.html',
    styleUrls: ['./job-submission.component.css']
})
export class JobSubmissionComponent implements OnInit {
    icons = Icons;

    // Data
    datasets: Dataset[] = [];
    models: Model[] = [];
    jobs: Job[] = [];

    // UI State
    loading = true;
    showCreateModal = false;
    submitting = false;
    error: string | null = null;

    // Form Data
    newJob: JobCreate = {
        dataset_id: 0,
        algorithm: '',
        params: {
            epochs: 100,
            batch_size: 32,
            learning_rate: 0.001
        }
    };

    selectedModelId: string = '';

    constructor(private api: ApiService) { }

    ngOnInit() {
        this.loadData();
    }

    loadData() {
        this.loading = true;
        this.error = null;

        // Load datasets, models, and jobs in parallel
        // In a real app we might want to use forkJoin here
        this.api.getDatasets().subscribe({
            next: (data) => this.datasets = data,
            error: () => console.error('Failed to load datasets')
        });

        this.api.getModels().subscribe({
            next: (data) => this.models = data,
            error: () => console.error('Failed to load models')
        });

        this.loadJobs();
    }

    loadJobs() {
        this.api.getJobs().subscribe({
            next: (data) => {
                this.jobs = data;
                this.loading = false;
            },
            error: (err) => {
                this.error = 'Failed to load jobs history';
                this.loading = false;
            }
        });
    }

    openCreateModal() {
        if (this.datasets.length > 0) {
            this.newJob.dataset_id = this.datasets[0].id;
        }
        this.showCreateModal = true;
    }

    createJob() {
        if (!this.newJob.dataset_id || !this.selectedModelId) return;

        // Find selected model to get algorithm name
        const model = this.models.find(m => m.id === this.selectedModelId);
        if (model) {
            this.newJob.algorithm = model.type;
        }

        this.submitting = true;
        this.api.createJob(this.newJob).subscribe({
            next: (job) => {
                this.jobs.unshift(job);
                this.submitting = false;
                this.showCreateModal = false;
                // Reset form defaults if needed
            },
            error: (err) => {
                alert('Failed to create job: ' + err.message);
                this.submitting = false;
            }
        });
    }

    getStatusClass(status: JobStatus): string {
        switch (status) {
            case JobStatus.RUNNING: return 'pm-badge-info';
            case JobStatus.COMPLETED: return 'pm-badge-success';
            case JobStatus.FAILED: return 'pm-badge-error';
            case JobStatus.QUEUED: return 'pm-badge-warning';
            default: return 'pm-badge-neutral';
        }
    }
}
