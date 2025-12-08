import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError, of } from 'rxjs';
import { catchError, retry } from 'rxjs/operators';
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

    constructor(private http: HttpClient) { }

    // Error handling
    private handleError(error: HttpErrorResponse) {
        let errorMessage = 'An unknown error occurred';
        if (error.error instanceof ErrorEvent) {
            // Client-side error
            errorMessage = error.error.message;
        } else {
            // Server-side error
            errorMessage = error.error?.detail || `Error ${error.status}: ${error.statusText}`;
        }
        console.error('API Error:', errorMessage);
        return throwError(() => new Error(errorMessage));
    }

    // === HEALTH ===
    getHealth(): Observable<SystemHealth> {
        return this.http.get<SystemHealth>(`${this.apiUrl.replace('/api/v1', '')}/health`).pipe(
            catchError(this.handleError)
        );
    }

    // === DATASETS ===
    getDatasets(): Observable<Dataset[]> {
        return this.http.get<Dataset[]>(`${this.apiUrl}/datasets/`).pipe(
            retry(1),
            catchError(this.handleError)
        );
    }

    getDataset(id: number): Observable<Dataset> {
        return this.http.get<Dataset>(`${this.apiUrl}/datasets/${id}`).pipe(
            catchError(this.handleError)
        );
    }

    uploadDataset(file: File, name: string, format: string): Observable<Dataset> {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('name', name);
        formData.append('format', format);
        return this.http.post<Dataset>(`${this.apiUrl}/datasets/`, formData).pipe(
            catchError(this.handleError)
        );
    }

    deleteDataset(id: number): Observable<void> {
        return this.http.delete<void>(`${this.apiUrl}/datasets/${id}`).pipe(
            catchError(this.handleError)
        );
    }

    // === JOBS ===
    getJobs(): Observable<Job[]> {
        return this.http.get<Job[]>(`${this.apiUrl}/jobs/`).pipe(
            retry(1),
            catchError(this.handleError)
        );
    }

    getJob(id: string): Observable<Job> {
        return this.http.get<Job>(`${this.apiUrl}/jobs/${id}`).pipe(
            catchError(this.handleError)
        );
    }

    createJob(job: JobCreate): Observable<Job> {
        return this.http.post<Job>(`${this.apiUrl}/jobs/`, job).pipe(
            catchError(this.handleError)
        );
    }

    // === MODELS ===
    getModels(): Observable<Model[]> {
        // Mock data for now - backend endpoint may need to be added
        return of([
            {
                id: 'unet-denoise-v4',
                name: 'UNet Denoiser V4',
                type: ModelType.UNET,
                version: '4.0.0',
                architecture: 'U-Net with ResNet encoder',
                status: ModelStatus.READY,
                created_at: new Date().toISOString(),
                metrics: { snr: 28.5, psnr: 35.2, ssim: 0.94 }
            },
            {
                id: 'ae-interpolate-v2',
                name: 'Autoencoder Interpolator V2',
                type: ModelType.AUTOENCODER,
                version: '2.1.0',
                architecture: 'Variational Autoencoder',
                status: ModelStatus.READY,
                created_at: new Date().toISOString(),
                metrics: { snr: 24.1, psnr: 31.8, ssim: 0.89 }
            },
            {
                id: 'gan-enhance-v1',
                name: 'GAN Signal Enhancer',
                type: ModelType.GAN,
                version: '1.0.0',
                architecture: 'Wasserstein GAN-GP',
                status: ModelStatus.TRAINING,
                created_at: new Date().toISOString()
            }
        ]);
    }

    trainModel(request: TrainingRequest): Observable<Job> {
        return this.http.post<Job>(`${this.apiUrl}/ml/train`, request).pipe(
            catchError(this.handleError)
        );
    }

    runInference(request: InferenceRequest): Observable<Job> {
        return this.http.post<Job>(`${this.apiUrl}/ml/predict`, request).pipe(
            catchError(this.handleError)
        );
    }

    // === SYSTEM ===
    getSystemMetrics(): Observable<SystemMetrics> {
        // Mock data - could be extended with real endpoints
        return of({
            active_jobs: 3,
            queued_jobs: 5,
            completed_jobs_24h: 24,
            total_datasets: 42,
            total_models: 4,
            storage_used_gb: 124.5
        });
    }

    // === DASHBOARD ===
    getDashboardStats(): Observable<DashboardStats> {
        // Aggregate from other endpoints or mock
        return of({
            datasets_count: 42,
            active_jobs: 3,
            models_count: 4,
            uptime_percent: 99.9
        });
    }

    getRecentActivity(): Observable<RecentActivity[]> {
        return of([
            {
                id: '1',
                type: 'job',
                title: 'Training: UNet-Denoise-V4',
                description: 'Model training in progress',
                status: 'running',
                timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString()
            },
            {
                id: '2',
                type: 'job',
                title: 'Inference: Gulf Block A',
                description: 'Reconstruction completed successfully',
                status: 'completed',
                timestamp: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString()
            },
            {
                id: '3',
                type: 'dataset',
                title: 'Dataset: North Sea Survey 2024',
                description: 'New dataset uploaded',
                status: 'completed',
                timestamp: new Date(Date.now() - 48 * 60 * 60 * 1000).toISOString()
            }
        ]);
    }
}
