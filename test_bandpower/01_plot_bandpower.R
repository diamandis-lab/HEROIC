library(readr)
library(ggplot2)
library(plotly)
library(EnvStats) #geoMean

setwd("/data/EEG")
library(reshape2)

source("R/00_environment.R")



data <- read_csv("purple_cat_test2_bandpower.csv")


channels<-unique(data$Chan)

bands<-c("Delta","Theta","Alpha","Sigma","Beta","Gamma")

bandpower<-list()
for(channel in channels){
  curr<-data[data$Chan==channel,]
  for(band in bands){
    curr.band<-as.numeric(t(curr[,band]))
    curr[,band]<-(curr.band/geoMean(curr.band))-1
  }
  
  bandpower[[channel]]<-curr
}





#ggplot(data=bandpower$CH1, aes(x=epoch_no, y=Gamma)) +
#  geom_line()


channel<-"CH4"

band.molten<-melt(bandpower[[channel]], id.vars="epoch_no", measure.vars=bands)

p<-ggplot(data=band.molten, aes(x=epoch_no, y=value, group=variable, color=variable)) +
  geom_line() +
  labs(title=channel) +
  theme_minimal()

ggplotly(p)

