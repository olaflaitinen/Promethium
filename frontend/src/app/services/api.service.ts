import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError, of, timer } from 'rxjs';
import { catchError, retry, timeout, map } from 'rxjs/operators';
import { environment } from '../../environments/environment';

// TypeScript interfaces for API responses

export interface Dataset {
    id: number;
    name: string;
    format: string;
    file_path: string;
    upload_time: string;
    metadata_json: Record<string, unknown>;
}

export interface DatasetCreate {
    name: string;
    format: string;
}

export interface Job {
    id: string;
    dataset_id: number;
    algorithm: string;
    status: JobStatus;
    params: Record<string, unknown>;
    created_at: string;
    started_at?: string;
    completed_at?: string;
    error_message?: string;
    result_path?: string;
}

export enum JobStatus {
    QUEUED = 'queued',
    RUNNING = 'running',
    COMPLETED = 'completed',
    FAILED = 'failed',
    CANCELLED = 'cancelled'
}

export interface JobCreate {
    dataset_id: number;
    algorithm: string;
    params?: Record<string, unknown>;
}

export interface Model {
    id: string;
    name: string;
    type: ModelType;
    version: string;
    architecture: string;
    status: ModelStatus;
    created_at: string;
    metrics?: ModelMetrics;
}

export enum ModelType {
    UNET = 'unet',
    AUTOENCODER = 'autoencoder',
    GAN = 'gan',
    TRANSFORMER = 'transformer'
}

export enum ModelStatus {
    READY = 'ready',
    TRAINING = 'training',
    PENDING = 'pending',
    FAILED = 'failed'
}

export interface ModelMetrics {
    snr?: number;
    mse?: number;
    psnr?: number;
    ssim?: number;
    training_loss?: number;
    validation_loss?: number;
}

export interface TrainingRequest {
    model_name: string;
    dataset_id: number;
    epochs: number;
    batch_size: number;
    learning_rate: number;
}

export interface InferenceRequest {
    model_id: string;
    dataset_id: number;
    output_name?: string;
}

export interface SystemHealth {
    status: 'ok' | 'degraded' | 'error';
    version: string;
    uptime?: number;
    database?: string;
    redis?: string;
}

export interface SystemMetrics {
    active_jobs: number;
    queued_jobs: number;
    completed_jobs_24h: number;
    total_datasets: number;
    total_models: number;
    storage_used_gb?: number;
}

export interface DashboardStats {
    datasets_count: number;
    active_jobs: number;
    models_count: number;
    uptime_percent: number;
}

export interface RecentActivity {
    id: string;
    type: 'job' | 'dataset' | 'model' | 'system';
    title: string;
    description: string;
    status: 'running' | 'completed' | 'failed' | 'pending';
    timestamp: string;
}

@Injectable({
    providedIn: 'root'
})
export class ApiService {
    private readonly apiUrl = environment.apiUrl;
    private backendAvailable = true;

    // Demo datasets for when backend is unavailable
    private readonly demoDatasets: Dataset[] = [
        {
            id: 1,
            name: 'Gulf of Mexico Survey 2024',
            format: 'SEGY',
            file_path: '/data/gom_2024.sgy',
            upload_time: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
            metadata_json: { traces: 24000, samples: 1500, sample_rate: 2 }
        },
        {
            id: 2,
            name: 'North Sea Block A',
            format: 'SEGY',
            file_path: '/data/north_sea_a.sgy',
            upload_time: new Date(Date.now() - 14 * 24 * 60 * 60 * 1000).toISOString(),
            metadata_json: { traces: 18500, samples: 2000, sample_rate: 4 }
        },
        {
            id: 3,
            name: 'Permian Basin Test',
            format: 'SAC',
            file_path: '/data/permian_test.sac',
            upload_time: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
            metadata_json: { traces: 8000, samples: 1000, sample_rate: 2 }
        },
        {
            id: 4,
            name: 'Mediterranean Survey 2023',
            format: 'miniSEED',
            file_path: '/data/med_2023.mseed',
            upload_time: new Date(Date.now() - 60 * 24 * 60 * 60 * 1000).toISOString(),
            metadata_json: { traces: 32000, samples: 2500, sample_rate: 1 }
        }
    ];

    // Demo jobs for when backend is unavailable
    private readonly demoJobs: Job[] = [
        {
            id: 'job-001',
            dataset_id: 1,
            algorithm: 'unet-denoise',
            status: JobStatus.COMPLETED,
            params: { epochs: 100, batch_size: 32 },
            created_at: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
            completed_at: new Date(Date.now() - 1.5 * 24 * 60 * 60 * 1000).toISOString(),
            result_path: '/results/job-001/'
        },
        {
            id: 'job-002',
            dataset_id: 2,
            algorithm: 'autoencoder-interpolate',
            status: JobStatus.RUNNING,
            params: { epochs: 50, batch_size: 64 },
            created_at: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
            started_at: new Date(Date.now() - 3 * 60 * 60 * 1000).toISOString()
        },
        {
            id: 'job-003',
            dataset_id: 1,
            algorithm: 'bandpass-filter',
            status: JobStatus.QUEUED,
            params: { freq_low: 10, freq_high: 60 },
            created_at: new Date(Date.now() - 30 * 60 * 1000).toISOString()
        },
        {
            id: 'job-004',
            dataset_id: 3,
            algorithm: 'deconvolution',
            status: JobStatus.FAILED,
            params: { iterations: 100 },
            created_at: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
            error_message: 'Out of memory during processing'
        }
    ];

    constructor(private http: HttpClient) { }

    // Error handling with fallback
    private handleError(error: HttpErrorResponse) {
        let errorMessage = 'An unknown error occurred';
        if (error.error instanceof ErrorEvent) {
            errorMessage = error.error.message;
        } else if (error.status === 0) {
            errorMessage = 'Backend server is not available';
            this.backendAvailable = false;
        } else {
            errorMessage = error.error?.detail || `Error ${error.status}: ${error.statusText}`;
        }
        console.error('API Error:', errorMessage);
        return throwError(() => new Error(errorMessage));
    }

    // Check if backend is available
    isBackendAvailable(): boolean {
        return this.backendAvailable;
    }

    // === HEALTH ===
    getHealth(): Observable<SystemHealth> {
        return this.http.get<SystemHealth>(`${this.apiUrl.replace('/api/v1', '')}/health`).pipe(
            timeout(5000),
            map(health => {
                this.backendAvailable = true;
                return health;
            }),
            catchError(() => {
                this.backendAvailable = false;
                return of({ status: 'error' as const, version: 'N/A', database: 'disconnected' });
            })
        );
    }

    // === DATASETS ===
    getDatasets(): Observable<Dataset[]> {
        return this.http.get<Dataset[]>(`${this.apiUrl}/datasets/`).pipe(
            timeout(5000),
            retry(1),
            map(datasets => {
                this.backendAvailable = true;
                return datasets;
            }),
            catchError(() => {
                this.backendAvailable = false;
                // Return demo data when backend is unavailable
                return of(this.demoDatasets);
            })
        );
    }

    getDataset(id: number): Observable<Dataset> {
        return this.http.get<Dataset>(`${this.apiUrl}/datasets/${id}`).pipe(
            timeout(5000),
            catchError(() => {
                const dataset = this.demoDatasets.find(d => d.id === id);
                if (dataset) return of(dataset);
                return throwError(() => new Error('Dataset not found'));
            })
        );
    }

    uploadDataset(file: File, name: string, format: string): Observable<Dataset> {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('name', name);
        formData.append('format', format);
        return this.http.post<Dataset>(`${this.apiUrl}/datasets/`, formData).pipe(
            timeout(60000),
            catchError(this.handleError.bind(this))
        );
    }

    deleteDataset(id: number): Observable<void> {
        return this.http.delete<void>(`${this.apiUrl}/datasets/${id}`).pipe(
            timeout(10000),
            catchError(this.handleError.bind(this))
        );
    }

    // === JOBS ===
    getJobs(): Observable<Job[]> {
        return this.http.get<Job[]>(`${this.apiUrl}/jobs/`).pipe(
            timeout(5000),
            retry(1),
            map(jobs => {
                this.backendAvailable = true;
                return jobs;
            }),
            catchError(() => {
                this.backendAvailable = false;
                return of(this.demoJobs);
            })
        );
    }

    getJob(id: string): Observable<Job> {
        return this.http.get<Job>(`${this.apiUrl}/jobs/${id}`).pipe(
            timeout(5000),
            catchError(() => {
                const job = this.demoJobs.find(j => j.id === id);
                if (job) return of(job);
                return throwError(() => new Error('Job not found'));
            })
        );
    }

    createJob(job: JobCreate): Observable<Job> {
        return this.http.post<Job>(`${this.apiUrl}/jobs/`, job).pipe(
            timeout(10000),
            catchError(this.handleError.bind(this))
        );
    }

    // === MODELS ===
    getModels(): Observable<Model[]> {
        // Demo models - ready to display immediately
        return of([
            {
                id: 'unet-denoise-v4',
                name: 'UNet Denoiser V4',
                type: ModelType.UNET,
                version: '4.0.0',
                architecture: 'U-Net with ResNet encoder, 32M params',
                status: ModelStatus.READY,
                created_at: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
                metrics: { snr: 28.5, psnr: 35.2, ssim: 0.94, mse: 0.0012 }
            },
            {
                id: 'ae-interpolate-v2',
                name: 'Autoencoder Interpolator V2',
                type: ModelType.AUTOENCODER,
                version: '2.1.0',
                architecture: 'Variational Autoencoder, 18M params',
                status: ModelStatus.READY,
                created_at: new Date(Date.now() - 60 * 24 * 60 * 60 * 1000).toISOString(),
                metrics: { snr: 24.1, psnr: 31.8, ssim: 0.89, mse: 0.0023 }
            },
            {
                id: 'gan-enhance-v1',
                name: 'GAN Signal Enhancer',
                type: ModelType.GAN,
                version: '1.0.0',
                architecture: 'Wasserstein GAN-GP, 45M params',
                status: ModelStatus.TRAINING,
                created_at: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
                metrics: { training_loss: 0.045, validation_loss: 0.052 }
            },
            {
                id: 'transformer-seismic-v1',
                name: 'Transformer Reconstructor',
                type: ModelType.TRANSFORMER,
                version: '1.0.0-beta',
                architecture: 'Vision Transformer, 86M params',
                status: ModelStatus.PENDING,
                created_at: new Date().toISOString()
            }
        ]);
    }

    trainModel(request: TrainingRequest): Observable<Job> {
        return this.http.post<Job>(`${this.apiUrl}/ml/train`, request).pipe(
            timeout(10000),
            catchError(this.handleError.bind(this))
        );
    }

    runInference(request: InferenceRequest): Observable<Job> {
        return this.http.post<Job>(`${this.apiUrl}/ml/predict`, request).pipe(
            timeout(10000),
            catchError(this.handleError.bind(this))
        );
    }

    // === SYSTEM ===
    getSystemMetrics(): Observable<SystemMetrics> {
        return of({
            active_jobs: 2,
            queued_jobs: 3,
            completed_jobs_24h: 18,
            total_datasets: this.demoDatasets.length,
            total_models: 4,
            storage_used_gb: 156.8
        });
    }

    // === DASHBOARD ===
    getDashboardStats(): Observable<DashboardStats> {
        return of({
            datasets_count: this.demoDatasets.length,
            active_jobs: 2,
            models_count: 4,
            uptime_percent: 99.7
        });
    }

    getRecentActivity(): Observable<RecentActivity[]> {
        return of([
            {
                id: '1',
                type: 'job',
                title: 'Training: GAN Signal Enhancer',
                description: 'Model training in progress (epoch 45/100)',
                status: 'running',
                timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString()
            },
            {
                id: '2',
                type: 'job',
                title: 'Inference: Gulf of Mexico Survey',
                description: 'Denoising completed successfully',
                status: 'completed',
                timestamp: new Date(Date.now() - 8 * 60 * 60 * 1000).toISOString()
            },
            {
                id: '3',
                type: 'dataset',
                title: 'Dataset: North Sea Block A',
                description: 'New SEG-Y dataset uploaded (18,500 traces)',
                status: 'completed',
                timestamp: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString()
            },
            {
                id: '4',
                type: 'model',
                title: 'Model: UNet Denoiser V4',
                description: 'Model deployed to production',
                status: 'completed',
                timestamp: new Date(Date.now() - 48 * 60 * 60 * 1000).toISOString()
            },
            {
                id: '5',
                type: 'system',
                title: 'System Update',
                description: 'Scheduled maintenance completed',
                status: 'completed',
                timestamp: new Date(Date.now() - 72 * 60 * 60 * 1000).toISOString()
            }
        ]);
    }
}
