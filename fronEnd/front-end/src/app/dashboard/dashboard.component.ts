// src/app/dashboard/dashboard.component.ts
import { Component, ElementRef, OnInit ,Renderer2} from '@angular/core';
import { SharedService } from '../services/shared/shared.service';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit {

  result: string = '';
  result2: any ='';

  machineLearning = false;
  visible = false;

  constructor(private sharedService: SharedService,private renderer: Renderer2,private elementRef: ElementRef) { }
  
  ngOnInit(): void {
    const aiToggle = this.elementRef.nativeElement.querySelector('.toggle-container');
    const chatToggle = this.elementRef.nativeElement.querySelector('.toggle-container-chat');

    if (aiToggle && chatToggle) {
      // Add hover event listener to .toggle-container
      this.renderer.listen(aiToggle, 'mouseenter', () => {
        this.renderer.setStyle(chatToggle, 'right', '158px'); // Move it left
      });

      // Reset the position when mouse leaves .toggle-container
      this.renderer.listen(aiToggle, 'mouseleave', () => {
        this.renderer.setStyle(chatToggle, 'right', '78px'); // Reset to original position
      });
    } else {
      console.error('Element not found: .toggle-container or .toggle-container-chat');
    }
    this.sharedService.currentResult.subscribe(result => {
      this.result = result;
    });
    this.sharedService.currentResultComp.subscribe(result => {
      this.result2 = result;
    });
  }

  toggleAI(): void {
    this.machineLearning = !this.machineLearning;
    if (this.machineLearning) {
      this.renderer.setStyle(document.body, 'background-color', '#e0f7fa');
    } else {
      this.renderer.removeStyle(document.body, 'background-color');
    }
  }
  toggleVisible(): void {
    this.visible = !this.visible;
  }

}
