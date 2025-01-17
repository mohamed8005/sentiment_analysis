// src/app/commande/commande.component.ts
import { Component, ElementRef, OnInit, ViewChild } from '@angular/core';
import { CdkDragDrop, moveItemInArray, transferArrayItem } from '@angular/cdk/drag-drop';
import { CommandeService } from '../services/commande/commande.service';
import { SharedService } from '../services/shared/shared.service';
import { MatSnackBar } from '@angular/material/snack-bar';

@Component({
  selector: 'app-commande',
  templateUrl: './commande.component.html',
  styleUrls: ['./commande.component.css']
})
export class CommandeComponent implements OnInit {

  @ViewChild('elementsContainer') elementsContainer!: ElementRef;
  @ViewChild('commandeContainer') commandeContainer!: ElementRef;

   elements: any[] = [
    // File
    { id: -1, name: 'Posts', label: 'Posts', background: '#2c315e', type: "file" },
    { id: 0, name: 'Comments', label: 'Comments', background: '#2c315e', type: "file" },
  
    // Sentiment Types
    { id: 1, name: 'Positifs', label: 'Positive', background: '#a5d6a7', type: "Sentiment" },
    { id: 2, name: 'Negatifs', label: 'Negative', background: '#ef9a9a', type: "Sentiment" },
    { id: 3, name: 'Neutres', label: 'Neutral', background: '#bdbdbd', type: "Sentiment" },
  
    // Metrics
    { id: 4, name: 'nombre', label: 'Count', background: '#7986cb', type: "Metrics" },
    { id: 5, name: 'pourcentage', label: 'Percentage', background: '#7986cb', type: "Metrics" },
    { id: 6, name: 'data', label: 'Data', background: '#7986cb', type: "export" },
  
    // Timeframes
    { id: 7, name: 'mois', label: 'Months', background: '#b39ddb', type: "Timeframes" },
    { id: 8, name: 'années', label: 'Years', background: '#b39ddb', type: "Timeframes" },
    { id: 9, name: 'saisons', label: 'Seasons', background: '#b39ddb', type: "Timeframes" },
  
    // Statistical Measures
    { id: 10, name: 'moyenne', label: 'Average', background: '#90caf9', type: "Measures" },
    { id: 11, name: 'médiane', label: 'Median', background: '#90caf9', type: "Measures" },
    { id: 12, name: 'maximal', label: 'Maximum', background: '#90caf9', type: "Measures" },
    { id: 13, name: 'minimal', label: 'Minimum', background: '#90caf9', type: "Measures" },
  
    // Filters/Context
    { id: 14, name: 'subreddit', label: 'Subreddit', background: '#ffcc80', type: "Filters" },
    { id: 15, name: 'user', label: 'User', background: '#ffcc80', type: "Filters" }
  ];
  
  
  

  commande: any[] = [];

  constructor(
    private commandeService: CommandeService,
    private sharedService: SharedService,
    private snackBar: MatSnackBar
  ) { }

  ngOnInit(): void {
  }

  /**
   * Calcule la distance euclidienne entre deux points.
   * @param x1 Coordonnée x du premier point
   * @param y1 Coordonnée y du premier point
   * @param x2 Coordonnée x du second point
   * @param y2 Coordonnée y du second point
   * @returns Distance euclidienne
   */
  private calculateDistance(x1: number, y1: number, x2: number, y2: number): number {
    const dx = x1 - x2;
    const dy = y1 - y2;
    return Math.sqrt(dx * dx + dy * dy);
  }

  /**
   * Gère l'événement de drop personnalisé en déterminant le conteneur le plus proche.
   * @param event Événement de drop
   */
  drop(event: CdkDragDrop<any[]>) {
    const dropX = event.dropPoint.x;
    const dropY = event.dropPoint.y;

    // Obtenir les positions des conteneurs
    const elementsRect = this.elementsContainer.nativeElement.getBoundingClientRect();
    const commandeRect = this.commandeContainer.nativeElement.getBoundingClientRect();

    // Calculer les centres des conteneurs
    const elementsCenterX = elementsRect.left + elementsRect.width / 2;
    const elementsCenterY = elementsRect.top + elementsRect.height / 2;

    const commandeCenterX = commandeRect.left + commandeRect.width / 2;
    const commandeCenterY = commandeRect.top + commandeRect.height / 2;

    // Calculer les distances
    const distanceToElements = this.calculateDistance(dropX, dropY, elementsCenterX, elementsCenterY);
    const distanceToCommande = this.calculateDistance(dropX, dropY, commandeCenterX, commandeCenterY);

    console.log(`Distance to Elements: ${distanceToElements}`);
    console.log(`Distance to Commande: ${distanceToCommande}`);

    // Déterminer le conteneur le plus proche
    let targetContainerId: string;
    if (distanceToElements < distanceToCommande) {
      targetContainerId = 'elements';
    } else {
      targetContainerId = 'commande';
    }

    console.log(`Target Container: ${targetContainerId}`);

    // Si le conteneur de destination n'est pas celui où l'utilisateur a lâché, transférer l'élément
    if (event.container.id !== targetContainerId) {
      // Trouver le bon conteneur
      const targetContainer = targetContainerId === 'elements' ? this.elements : this.commande;

      // Transférer l'élément
      transferArrayItem(
        event.previousContainer.data,
        targetContainer,
        event.previousIndex,
        targetContainer.length
      );

      // Mettre à jour l'état
      this.elements = [...this.elements];
      this.commande = [...this.commande];

      // Afficher une notification
      if (targetContainerId === 'commande') {
        this.snackBar.open('Élément ajouté à la commande.', 'Fermer', { duration: 2000 });
      } else {
        this.snackBar.open('Élément retiré de la commande.', 'Fermer', { duration: 2000 });
      }
    } else {
      // Réorganiser les éléments dans la même liste
      moveItemInArray(event.container.data, event.previousIndex, event.currentIndex);
      this.snackBar.open('Élément réorganisé.', 'Fermer', { duration: 2000 });
    }
  }

  /**
   * Envoie la commande au backend.
   */
  async envoyer() {
    if (this.commande.length === 0) {
      this.snackBar.open('Aucune commande à envoyer.', 'Fermer', { duration: 3000 });
      return;
    }

    const instruction = this.commande.map(item => item.name).join(', ');
    const payload: any = {
      files: [],
      sentiments: [],
      metrics: [],
      timeframes: [],
      measures: [],
      filters: [],
      rankings: [],
      export: [],
    };
    this.commande.forEach(item => {
      switch (item.type) {
        case 'file':
          payload.files.push(item.name.toLowerCase()); // Add to files
          break;
        case 'Sentiment':
          payload.sentiments.push(item.name.toLowerCase()); // Add to sentiments
          break;
        case 'Metrics':
          payload.metrics.push(item.name.toLowerCase()); // Add to metrics
          break;
        case 'Timeframes':
          payload.timeframes.push(item.name.toLowerCase()); // Add to timeframes
          break;
        case 'Measures':
          payload.measures.push(item.name.toLowerCase()); // Add to measures
          break;
        case 'Filters':
          payload.filters.push(item.name.toLowerCase()); // Add to filters
          break;
        case 'Rankings':
          payload.rankings.push(item.name.toLowerCase()); // Add to rankings
          break;
        case 'export':
          payload.export.push(item.name.toLowerCase()); // Add to rankings
          break;
      }
    });
    const payload2 = { "instructions": payload };
    console.log('Payload:', payload2);
    this.sharedService.loadingPage(true)
    if(payload2.instructions.export.length>0){
      await this.commandeService.export(payload2).subscribe({
        next: (blob) => {
          const url = window.URL.createObjectURL(blob);
          const anchor = document.createElement('a');
          anchor.href = url;
          anchor.download = 'exported_data.csv'; // File name
          anchor.click();
          window.URL.revokeObjectURL(url);
        },
        error: (err) => {
          console.error('Error downloading CSV:', err);
        }
      });
    }
    this.commandeService.envoyerCommande(payload2).subscribe({
      next: (response) => {
        console.log('Commande envoyée avec succès', response);
        
        // Update the shared service result
        this.sharedService.updateResult2({results:response['results']});
        this.sharedService.updateResult('');
        
        // Show a success notification
        this.snackBar.open('Commande envoyée avec succès!', 'Fermer', { duration: 3000 });
        
        // Clear the commande array after successful submission
        // this.commande = [];
        this.sharedService.loadingPage(false)
      },
      error: (error) => {
        console.error('Erreur lors de l\'envoi de la commande', error);
        
        this.sharedService.loadingPage(false)
        // Update the shared service with error details
        this.sharedService.updateResult(`Erreur lors de l'envoi de la commande : ${error.message}`);
    
        // Show an error notification
        this.snackBar.open('Erreur lors de l\'envoi de la commande.', 'Fermer', { duration: 3000 });
      },
    });
   
    
    // this.elements=this.elements.concat(this.commande).sort((a, b) => a.id - b.id);;
    // this.commande=[]
  }
  resetCommande() {
    // Return all commande items to the elements list if you want them back
    this.elements = this.elements.concat(this.commande).sort((a, b) => a.id - b.id);;
    this.commande = [];
    
    // Optionally, show a notification
    this.snackBar.open('Commande réinitialisée avec succès.', 'Fermer', { duration: 2000 });
  }
  
}