import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-seismic-viewer',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="viewer-container">
        <h2>Interactive Visualization</h2>
        <div class="placeholder-plot">
            <p>Seismic Data Visualization Module</p>
            <p>Select a completed job to visualize results.</p>
            <!-- Plotly integration would go here -->
        </div>
    </div>
  `,
  styles: [`
    .viewer-container { padding: 20px; }
    .placeholder-plot { 
        border: 2px dashed #ccc; 
        height: 400px; 
        display: flex; 
        flex-direction: column;
        justify-content: center; 
        align-items: center; 
        background: #fafafa;
    }
  `]
})
export class SeismicViewerComponent { }
