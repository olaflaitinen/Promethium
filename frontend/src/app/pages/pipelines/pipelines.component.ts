import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { Icons } from '../../shared/icons';

interface Pipeline {
    id: number;
    name: string;
    description: string;
    config: object;
    created_at: string;
    status: 'active' | 'draft' | 'archived';
}

@Component({
    selector: 'app-pipelines',
    standalone: true,
    imports: [CommonModule, FormsModule, RouterLink],
    templateUrl: './pipelines.component.html',
    styleUrls: ['./pipelines.component.css']
})
export class PipelinesComponent implements OnInit {
    icons = Icons;
    pipelines: Pipeline[] = [];
    loading = true;
    showEditor = false;
    editingPipeline: Pipeline | null = null;
    configText = '';

    // Demo data
    private demoPipelines: Pipeline[] = [
        {
            id: 1,
            name: 'Standard Denoising',
            description: 'Industry-standard denoising workflow with Wiener filter and U-Net',
            config: {
                steps: [
                    { name: 'bandpass_filter', params: { low: 5, high: 80 } },
                    { name: 'wiener_filter', params: { noise_estimate: 'auto' } },
                    { name: 'unet_denoise', params: { model: 'unet-v4' } }
                ]
            },
            created_at: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
            status: 'active'
        },
        {
            id: 2,
            name: 'Trace Interpolation',
            description: 'Missing trace reconstruction using autoencoder',
            config: {
                steps: [
                    { name: 'normalize', params: {} },
                    { name: 'autoencoder_interpolate', params: { model: 'ae-v2' } },
                    { name: 'denormalize', params: {} }
                ]
            },
            created_at: new Date(Date.now() - 14 * 24 * 60 * 60 * 1000).toISOString(),
            status: 'active'
        },
        {
            id: 3,
            name: 'Full Reconstruction',
            description: 'Complete pipeline including denoising, interpolation, and enhancement',
            config: {
                steps: [
                    { name: 'bandpass_filter', params: { low: 3, high: 100 } },
                    { name: 'wiener_filter', params: {} },
                    { name: 'matrix_completion', params: { algorithm: 'ista' } },
                    { name: 'unet_denoise', params: {} },
                    { name: 'quality_assessment', params: {} }
                ]
            },
            created_at: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
            status: 'draft'
        }
    ];

    ngOnInit() {
        this.loadPipelines();
    }

    loadPipelines() {
        this.loading = true;
        // Simulate API call
        setTimeout(() => {
            this.pipelines = this.demoPipelines;
            this.loading = false;
        }, 500);
    }

    openEditor(pipeline?: Pipeline) {
        this.showEditor = true;
        if (pipeline) {
            this.editingPipeline = pipeline;
            this.configText = JSON.stringify(pipeline.config, null, 2);
        } else {
            this.editingPipeline = null;
            this.configText = JSON.stringify({
                steps: [
                    { name: 'step_name', params: {} }
                ]
            }, null, 2);
        }
    }

    closeEditor() {
        this.showEditor = false;
        this.editingPipeline = null;
        this.configText = '';
    }

    savePipeline() {
        try {
            JSON.parse(this.configText);
            // Would save via API
            this.closeEditor();
            this.loadPipelines();
        } catch (e) {
            alert('Invalid JSON configuration');
        }
    }

    getStatusClass(status: string): string {
        switch (status) {
            case 'active': return 'status-active';
            case 'draft': return 'status-draft';
            case 'archived': return 'status-archived';
            default: return '';
        }
    }

    formatDate(date: string): string {
        return new Date(date).toLocaleDateString();
    }
}
