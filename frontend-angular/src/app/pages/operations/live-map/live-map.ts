import { Component, ElementRef, ViewChild, AfterViewInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import * as L from 'leaflet';

@Component({
  selector: 'app-live-map',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './live-map.html',
  styleUrl: './live-map.scss'
})
export class LiveMapComponent implements AfterViewInit {
  @ViewChild('map') mapContainer!: ElementRef;
  map!: L.Map;

  ngAfterViewInit() {
    this.initMap();
  }

  private initMap(): void {
    this.map = L.map(this.mapContainer.nativeElement).setView([-25.4284, -49.2733], 13); // Curitiba

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors'
    }).addTo(this.map);
  }
}
