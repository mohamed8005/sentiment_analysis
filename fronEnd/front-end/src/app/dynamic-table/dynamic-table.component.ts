import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-dynamic-table',
  templateUrl: './dynamic-table.component.html',
  styleUrls: ['./dynamic-table.component.css']
})
export class DynamicTableComponent {
  @Input() data: any = {}; // The JSON data to display

  // Helper to determine if a value is an object (nested level)
  isObject(value: any): boolean {
    return value && typeof value === 'object' && !Array.isArray(value);
  }

  // Helper to get object keys
  objectKeys(obj: any): string[] {
    return Object.keys(obj);
  }
}
