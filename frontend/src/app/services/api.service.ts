import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface Dataset {
    id: number;
    name: string;
    format: string;
    upload_time: string;
    file_path: string;
}

export interface Job {
    id: string;
    status: string;
    algorithm: string;
    created_at: string;
    result_path?: string;
    error_message?: string;
    params?: any;
}

@Injectable({
    providedIn: 'root'
})
export class ApiService {
    private customApiUrl = '/api/v1'; // Proxy forwards to localhost:8000

    constructor(private http: HttpClient) { }

    getDatasets(): Observable<Dataset[]> {
        return this.http.get<Dataset[]>(`${this.customApiUrl}/datasets/`);
    }

    uploadDataset(file: File, name: string, format: string): Observable<Dataset> {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('name', name);
        formData.append('format', format);
        return this.http.post<Dataset>(`${this.customApiUrl}/datasets/`, formData);
    }

    submitJob(datasetId: number, algorithm: string, params: any): Observable<any> {
        return this.http.post(`${this.customApiUrl}/jobs/`, {
            dataset_id: datasetId,
            algorithm,
            params
        });
    }

    getJobs(): Observable<Job[]> {
        return this.http.get<Job[]>(`${this.customApiUrl}/jobs/`);
    }

    getJob(id: string): Observable<Job> {
        return this.http.get<Job>(`${this.customApiUrl}/jobs/${id}`);
    }
}
