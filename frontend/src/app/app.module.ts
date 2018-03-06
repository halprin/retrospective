import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';


import { AppComponent } from './app.component';
import { NavigationBarComponent } from './navigation-bar/navigation-bar.component';
import { AppRoutingModule } from './/app-routing.module';
import { StartRetroComponent } from './start-retro/start-retro.component';
import { JoinRetroComponent } from './join-retro/join-retro.component';


@NgModule({
  declarations: [
    AppComponent,
    NavigationBarComponent,
    StartRetroComponent,
    JoinRetroComponent,
  ],
  imports: [
    BrowserModule,
    AppRoutingModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
