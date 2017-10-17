#!/usr/bin/env Rscript

library(ggplot2)

args = commandArgs(trailingOnly=TRUE)

rel.abundance <- read.delim(args[1], header=F, row.names=1)
genome.fraction <- read.delim(args[2], skip=1, header=F, sep="", row.names=1)
out.file <- args[3]


genome.fraction$V2 <- as.numeric(as.character(genome.fraction$V2))
genome.fraction$V2[is.na(genome.fraction$V2)] <- 0

genome.fraction.sorted <- genome.fraction[match(rownames(rel.abundance), rownames(genome.fraction)),]

sample <- cbind(rel.abundance, genome.fraction.sorted)

p = ggplot(sample, aes(x=log10(V2), y=genome.fraction.sorted))
p = p + geom_point(size=3)
p = p + theme(axis.text.x = element_text(angle = 90, hjust = 1))
p = p + theme_bw()

pdf(out.file, width=6, height=4)
p
dev.off()