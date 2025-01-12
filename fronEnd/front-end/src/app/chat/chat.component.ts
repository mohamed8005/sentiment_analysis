// src/app/chat/chat.component.ts
import { Component, Input, OnInit } from '@angular/core';
import { ChatService } from '../services/chat/chat.service';
import { SharedService } from '../services/shared/shared.service';

interface Message {
  text: string;
  user: boolean; // true si l'utilisateur, false si le bot
  machineLearning?: boolean
}

@Component({
  selector: 'app-chat',
  templateUrl: './chat.component.html',
  styleUrls: ['./chat.component.css']
})
export class ChatComponent implements OnInit {

  messages: Message[] = [];
  nouveauMessage: string = '';
  @Input() machineLearning = false;
  @Input() visible = true;
  constructor(
    private chatService: ChatService,
    private sharedService: SharedService
  ) { }

  ngOnInit(): void {
  }

  envoyerMessage() {
    if (this.nouveauMessage.trim() === '') return;

    // Ajouter le message de l'utilisateur
    // this.messages.push({ text: this.nouveauMessage, user: true });
    
    const message = { sentence: this.nouveauMessage, user: false ,machineLearning: this.machineLearning};
    this.nouveauMessage = '';
console.log({ text: this.nouveauMessage, user: false ,machineLearning: this.machineLearning})
    // Envoyer le message au service et recevoir une réponse
    this.sharedService.loadingPage(true)
    this.chatService.envoyerMessage(message).subscribe({
      next: (reponse) => {
        // Add the AI response to messages
        console.log('chat envoyée avec succès', reponse);
        // this.messages.push({ text: reponse.reply, user: false, machineLearning: this.machineLearning });
        this.sharedService.loadingPage(false)
        // Update the shared service result
        this.sharedService.updateResult(`cette phrase a un sentiment : "${reponse.sentiment}" avec un score total de: ${reponse.compound} `);
        this.sharedService.updateResult2("");
      },
      error: (error) => {
        console.error('Erreur lors de l\'envoi du message', error);
        this.sharedService.loadingPage(false)
        // Update the shared service with error details
        this.sharedService.updateResult(`Erreur lors de l'envoi du message : ${error.message}`);
      },
    });
    
  }

}
