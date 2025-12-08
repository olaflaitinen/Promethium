import { Component, AfterViewInit, ViewChild, ElementRef, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService, Dataset, Job } from '../../services/api.service';
import { Icons } from '../../shared/icons';

@Component({
    selector: 'app-visualization',
    standalone: true,
    imports: [CommonModule, FormsModule],
    templateUrl: './visualization.component.html',
    styleUrls: ['./visualization.component.css']
})
export class VisualizationComponent implements OnInit, AfterViewInit {
    icons = Icons;

    // View References
    @ViewChild('seismicCanvas') seismicCanvas!: ElementRef<HTMLCanvasElement>;

    // Data
    datasets: Dataset[] = [];
    jobs: Job[] = [];

    // UI State
    loading = true;
    rendering = false;

    // Controls
    controls = {
        datasetId: 0,
        jobId: '',
        viewMode: 'waveform' as 'waveform' | 'spectrogram' | 'difference',
        gain: 1.0,
        colormap: 'seismic',
        showGrid: true
    };

    constructor(private api: ApiService) { }

    ngOnInit() {
        this.loadData();
    }

    ngAfterViewInit() {
        // Initialize visualization context if needed
        this.resizeCanvas();
        window.addEventListener('resize', () => this.resizeCanvas());
    }

    loadData() {
        this.loading = true;
        // Mock loading data
        this.api.getDatasets().subscribe({
            next: (data) => {
                this.datasets = data;
                if (data.length > 0) this.controls.datasetId = data[0].id;
                this.loading = false;
                setTimeout(() => this.renderPlaceholder(), 100);
            },
            error: () => this.loading = false
        });
    }

    resizeCanvas() {
        if (!this.seismicCanvas) return;
        const canvas = this.seismicCanvas.nativeElement;
        const container = canvas.parentElement;
        if (container) {
            canvas.width = container.clientWidth;
            canvas.height = container.clientHeight;
            this.renderPlaceholder();
        }
    }

    renderPlaceholder() {
        if (!this.seismicCanvas) return;
        const ctx = this.seismicCanvas.nativeElement.getContext('2d');
        if (!ctx) return;

        const w = ctx.canvas.width;
        const h = ctx.canvas.height;

        // Clear
        ctx.fillStyle = '#050B24';
        ctx.fillRect(0, 0, w, h);

        // Draw Grid
        if (this.controls.showGrid) {
            ctx.strokeStyle = '#1F2937';
            ctx.lineWidth = 1;
            ctx.beginPath();
            for (let x = 0; x < w; x += 50) { ctx.moveTo(x, 0); ctx.lineTo(x, h); }
            for (let y = 0; y < h; y += 50) { ctx.moveTo(0, y); ctx.lineTo(w, y); }
            ctx.stroke();
        }

        // Draw Simulated Seismic Wiggle Traces
        ctx.strokeStyle = '#00F0FF';
        ctx.lineWidth = 1.5;
        ctx.beginPath();

        const numTraces = Math.floor(w / 30);
        for (let i = 0; i < numTraces; i++) {
            const xBase = i * 30 + 15;
            ctx.moveTo(xBase, 0);

            for (let y = 0; y < h; y += 2) {
                // Generate synthetic seismic wave
                const amp = Math.exp(-0.00005 * (y - h / 2) ** 2) * 20 * this.controls.gain;
                const freq = 0.05;
                const offset = Math.sin(y * freq + i) * amp * Math.random();
                ctx.lineTo(xBase + offset, y);
            }
        }
        ctx.stroke();

        // Add dummy annotation/overlay
        ctx.fillStyle = 'rgba(0, 240, 255, 0.1)';
        ctx.fillRect(100, 100, 200, h - 200);
        ctx.strokeStyle = 'rgba(0, 240, 255, 0.5)';
        ctx.strokeRect(100, 100, 200, h - 200);

        ctx.fillStyle = '#00F0FF';
        ctx.font = '12px Inter';
        ctx.fillText('Detected Feature Zone', 105, 95);
    }
}
