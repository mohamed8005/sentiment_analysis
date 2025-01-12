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
    //file
    { id: -1, name: 'Posts', background: '#2c315e' ,type:"file"},   // Green 200
    { id: 0, name: 'Comments', background: '#2c315e'  ,type:"file"},
    // Sentiment Types
    { id: 1, name: 'Positifs', background: '#a5d6a7' ,type:"Sentiment"},   // Green 200
    { id: 2, name: 'Negatifs', background: '#ef9a9a' ,type:"Sentiment"},   // Red 200
    { id: 3, name: 'Neutres', background: '#bdbdbd' ,type:"Sentiment"},    // Grey 400
  
    // Metrics
    { id: 4, name: 'nombre', background: '#7986cb' ,type:"Metrics"},      // Indigo 300
    { id: 5, name: 'pourcentage', background: '#7986cb' ,type:"Metrics"},
    { id: 5, name: 'data', background: '#7986cb' ,type:"export"},
  
    // Timeframes
    // { id: 6, name: 'temps', background: '#b39ddb' ,type:"Timeframes"},    // Deep Purple 200
    // { id: 7, name: 'jours', background: '#b39ddb' ,type:"Timeframes"},
    { id: 8, name: 'mois', background: '#b39ddb' ,type:"Timeframes"},
    // { id: 9, name: 'durée', background: '#b39ddb' ,type:"Timeframes"},
    // { id: 10, name: 'heures', background: '#b39ddb' ,type:"Timeframes"},
    // { id: 11, name: 'semaines', background: '#b39ddb' ,type:"Timeframes"},
    { id: 12, name: 'années', background: '#b39ddb' ,type:"Timeframes"},
    { id: 13, name: 'saisons', background: '#b39ddb' ,type:"Timeframes"},
  
    // Statistical Measures
    { id: 14, name: 'moyenne', background: '#90caf9' ,type:"Measures"},   // Blue 200
    { id: 15, name: 'médiane', background: '#90caf9' ,type:"Measures"},
    { id: 16, name: 'maximal', background: '#90caf9' ,type:"Measures"},
    { id: 17, name: 'minimal', background: '#90caf9' ,type:"Measures"},
    // { id: 18, name: 'tendance', background: '#90caf9' ,type:"Measures"},
    // { id: 19, name: 'évolution', background: '#90caf9' ,type:"Measures"},
    // { id: 20, name: 'augmentation', background: '#90caf9' ,type:"Measures"},
    // { id: 21, name: 'diminution', background: '#90caf9' ,type:"Measures"},
  
    // Filters/Context
    // { id: 22, name: 'filtrer', background: '#ffcc80' ,type:"Filters"},   // Orange 200
    // { id: 23, name: 'mot-clé', background: '#ffcc80' ,type:"Filters"},
    { id: 24, name: 'subreddit', background: '#ffcc80' ,type:"Filters"},
    { id: 24, name: 'user', background: '#ffcc80' ,type:"Filters"},
    // { id: 25, name: 'catégorie', background: '#ffcc80' ,type:"Filters"},
  
    // Comparisons/Rankings
    // { id: 26, name: 'comparaison', background: '#bcaaa4' ,type:"Rankings"}, // Brown 200
    // { id: 27, name: 'classement', background: '#bcaaa4' ,type:"Rankings"},
    // { id: 28, name: 'top', background: '#bcaaa4' ,type:"Rankings"},
    // { id: 29, name: 'plus élevé', background: '#bcaaa4' ,type:"Rankings"},
    // { id: 30, name: 'plus bas', background: '#bcaaa4' ,type:"Rankings"}
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
          anchor.download = 'exported_data.xlsx'; // File name
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
        this.commande = [];
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
   
    
    this.elements=this.elements.concat(this.commande).sort((a, b) => a.id - b.id);;
    this.commande=[]
  }
  resetCommande() {
    // Return all commande items to the elements list if you want them back
    this.elements = this.elements.concat(this.commande).sort((a, b) => a.id - b.id);;
    this.commande = [];
    
    // Optionally, show a notification
    this.snackBar.open('Commande réinitialisée avec succès.', 'Fermer', { duration: 2000 });
  }
  
}