import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-dynamic-tree',
  templateUrl: './dynamic-tree.component.html',
  styleUrls: ['./dynamic-tree.component.css']
})
export class DynamicTreeComponent {
  @Input() data: any = {}; // The JSON data received from the API
  @Input() depth: number = 0;
  // Helper to determine if a value is an object (for nested rows)
  isObject(value: any): boolean {
    return value && typeof value === 'object' && !Array.isArray(value);
  }

  // Helper to get object keys
  objectKeys(obj: any): string[] {
    return Object.keys(obj);
  }
}
