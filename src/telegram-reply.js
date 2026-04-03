function isMessageNotFound(error) {
  const description =
    error?.response?.description ?? '';
  const message =
    error instanceof Error
      ? error.message
      : String(error ?? '');

  return description.includes('message to edit not found')
    || message.includes('message to edit not found');
}


export async function replaceWaitingMessage(
  ctx,
  messageId,
  text,
) {
  try {
    await ctx.telegram.editMessageText(
      ctx.chat.id,
      messageId,
      null,
      text,
    );
  } catch (error) {
    if (isMessageNotFound(error)) {
      await ctx.reply(text);
      return;
    }

    throw error;
  }
}
